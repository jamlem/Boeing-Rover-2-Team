//Jeremy Lim
//2/22/17
//Code for arduino hw interface to motors, sensors & servos
//For comm testing, send the E-stop command to turn on LED 13, and reset wheel odometry to turn off LED13
//Boeing Capstone 2 team.


#define MAGIC_NUM 0x32  //Used as the first byte of every valid message.


//pin assignments

#define BATTERY_PIN A0  //analog pin used to read battery voltage.
//Encoder pin pairs:
//Encoder 1: 8 and 3//Right motor
//Encoder 2: 9 and 4//Left Motor
//Encoder 3: 10 and 5
//Encoder 4: 11 and 6

//Program frequency
//Fraction of a second.
const float prog_delay = 0.01;//10 ms period currently.

//Encoder counts
volatile long enc1;
volatile long enc2;

//Bytes used for the ISR
volatile byte pinState = 0x00;
volatile byte prevPinState = 0x00;
volatile byte checkVal;
volatile byte checkState = 0x00;


int pinval;



long e1;
long e2;

//Persistent variables

//Velocities, in cm/s, for each wheel.
float velocityLeft;
float velocityRight;
float angularVelocity;

float displacementX;
float displacementY;
float displacementAngular;

float batteryVoltage;
float IRheading;
float IRelevation;

byte  statusByte;

//Current velocity commands
float commandLeft;
float commandRight;

//Global variable; used to keep track of the previous motor speed update time.
long prevTime;

//Physical constants
const float batteryVoltageConversion = 1.0;//Arbitrary for now.

void setup()
{
  //Set up the baudrate. 8N1
  prevTime = millis();
  Serial.begin(115200);
  
  //Set the pin modes for reading from the encoder.
  pinMode(3,INPUT);
  pinMode(4,INPUT);
  
  pinMode(8,INPUT);
  pinMode(9,INPUT);
  
  //initialize variables.
  e1 = 0;//Right
  e2 = 0;//Left
  
  commandLeft = 0;
  commandRight = 0;
  
  setupPCIs();
  delay(50);
}

//AVR specific code for enabling pin-change
// interrupts
void setupPCIs()
{
  cli();//Turn off interrupts right now
  PCICR |= (1 << PCIE0);//Enable the interrupt for the PCIE0 group of pins.
  //This enables the interrupts for pins 8-13 (and 2 other pins) on an arduino uno for pin change interrupts
  //We'll specifically enable pins 8, 9, 10, and 11.
  PCMSK0 |= (1 << PCINT0) | (1 << PCINT1); //| (1 << PCINT2) | (1 << PCINT3);
  sei();//Re-enable interrupts
}

//Interrupt service routine for those 4 pins.
ISR (PCINT0_vect)
{
  //save our current pin state, into this byte.
  pinState = (digitalRead(8) << PCINT0);// | (digitalRead(9) << PCINT1) | (digitalRead(10) << PCINT2) | (digitalRead(11) << PCINT3);
  //find out which pins changed, compared to previously.
  checkState = pinState ^ prevPinState;
  //gray code:
  //8 3
  //---
  //0 1
  //1 1
  //1 0
  //0 0
  //enc1 = 20;
  
  //Encoder 1 changed
  if ((1 << PCINT0) & checkState)
  {
    //Encoder 1 checking. (3 and 8)
    checkVal = digitalRead(3);
    if (digitalRead(8))//pulse high
    {
      if (checkVal)
      {
        enc1++;
      }
      else
      {
        enc1--;
      }
    }
    else//Opposite direction...
    {
      if (checkVal)
      {
        enc1--;
      }
      else
      {
        enc1++;
      }
    }
  }
  if ((1 << PCINT1) & checkState)
  {
    //Encoder 2(9 and 4)
    checkVal = digitalRead(4);
    if (digitalRead(9))//pulse high
    {
      if (checkVal)
      {
        enc2++;
      }
      else
      {
        enc2--;
      }
    }
    else//Opposite direction...
    {
      if (checkVal)
      {
        enc2--;
      }
      else
      {
        enc2++;
      }
    }
  }
  
  
  //update the previous value.
  prevPinState = pinState;
}


void loop()
{
  
  //Read sensors, assign motor commands.
  //Update battery voltage reading.
  batteryVoltage = analogRead(BATTERY_PIN)*batteryVoltageConversion;
  
  //Get status from IR system.
  //This will depend on what system we get.
  
  //Update motor velocities.
  //If performance issues occure, we will
  float time_delay = (millis() - prevTime)/1000.0;
  updateMotorSpeeds(time_delay);
  prevTime = millis();
 
  
  //Read any possible command updates.
  //This is nearly non-blocking.
  checkForCommand();
  updateMotorCommands(commandLeft, commandRight);
  
  
  //Update the raspberry pi on the status.
  //This is completely asynchronous with recieving commands.
  //May need to decrease this frequency.
  //sendStatusUpdate();
  delay(40);//Main program runs every 10ms.
}

//Handle's the arduino sending a status command back to the raspberry pi
void sendStatusUpdate()
{
  byte sendBuffer[38];
  //Set up our message, according to the desired format.
  sendBuffer[0] = 0x32;
  //Right wheel velocity
  floatToBigEndian((byte*)&velocityRight,sendBuffer+1);
  //Left wheel Velocity
  floatToBigEndian((byte*)&velocityLeft,sendBuffer+5);
  //Calculated angular velocity
  floatToBigEndian((byte*)&angularVelocity,sendBuffer+9);
  //X displacement
  floatToBigEndian((byte*)&displacementX,sendBuffer+13);
  //Y displacement
  floatToBigEndian((byte*)&displacementY,sendBuffer+17);
  //Angular displacement
  floatToBigEndian((byte*)&displacementAngular,sendBuffer+21);
  //Battery Voltage
  floatToBigEndian((byte*)&batteryVoltage,sendBuffer+25);
  //Ir Elevation
  floatToBigEndian((byte*)&IRelevation,sendBuffer+29);
  //Ir Heading
  floatToBigEndian((byte*)&IRheading,sendBuffer+33);
  //Status byte.
  sendBuffer[37] = statusByte;
  
  //Write our command on the serial line.
  Serial.write(sendBuffer,38);
}

//Checks the serial line for any command updates
//Returns the read state, to be used for subsequent command checks.
void checkForCommand()
{
  byte byteBuf[8];
  //Check if anything is on the serial buffer
  int readyBytes = Serial.available();
  if (readyBytes < 2)
    return;//nothing to read.
  
  byte current = Serial.read();//check if the next byte is valid.
  if (current != MAGIC_NUM)
    return;//Not a valid command
    
  current = Serial.read();//check for the command byte.
  if (current == 0)//speed assignment
  {
    //for now, we'll block until we get the bytes we need. If performance becomes
    //and issue, this can be re-written non-blocking
    while (Serial.available() < 8);
    //TODO: Read command from raspberry pi.
    Serial.readBytes((char*)byteBuf,8);
    //Global command vars.
    bigEndianToFloat(&byteBuf[0],&commandRight);
    bigEndianToFloat(&byteBuf[4],&commandLeft);
  }
  else if(current == 0x1)
  {
    //reset our wheel odometry
    displacementX = 0.0;
    displacementY = 0.0;
    displacementAngular = 0.0;
    //turn off pin 13 LED
    pinMode(13,OUTPUT);
    digitalWrite(13,LOW);
  }
  else if(current == 0x2)
  {
    //Stop all actuators(software E-stop!)
    commandLeft = 0;
    commandRight = 0;
    //ton on pin 13 LED
    pinMode(13,OUTPUT);
    digitalWrite(13,HIGH);
  }
  else
  {
    return;//invalid command.
  }
  
  //Send a response, after a valid command.
  sendStatusUpdate();
}

//Takes a 4-byte float at the given location, and 
//transforms it into network byte order (big endian)
//Arduino is little endian!
void floatToBigEndian(byte * numberLoc, byte * bufLoc)
{
  //reverse byte order
  bufLoc[0] = numberLoc[3];
  bufLoc[1] = numberLoc[2];
  bufLoc[2] = numberLoc[1];
  bufLoc[3] = numberLoc[0];
}

//Transform a float in big endian to little endian
//so the arduino can read it.
float bigEndianToFloat(byte * numberLoc, float* writeNum)
{
  byte tempBuffer[4];
  //reverse byte order
  ((byte*)writeNum)[0] = numberLoc[3];
  ((byte*)writeNum)[1] = numberLoc[2];
  ((byte*)writeNum)[2] = numberLoc[1];
  ((byte*)writeNum)[3] = numberLoc[0];
  //Re-cast to float (hopefully!)
  //return (float)tempBuffer;
}
