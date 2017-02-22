//Jeremy Lim
//2/22/17
//Code for arduino hw interface to motors, sensors & servos
//Boeing Capstone 2 team.

//Encoder pin pairs:
//Encoder 1: 8 and 3
//Encoder 2: 9 and 4
//Encoder 3: 10 and 5
//Encoder 4: 11 and 6

volatile long enc1;
volatile long enc2;
volatile long enc3;
volatile long enc4;

volatile byte pinState = 0x00;
volatile byte prevPinState = 0x00;
volatile byte checkVal;
volatile byte checkState = 0x00;
int pinval;

long e1;
long e2;
long e3;
long e4;

void setup()
{
  Serial.begin(9600);
  pinMode(3,INPUT);
  pinMode(4,INPUT);
  pinMode(5,INPUT);
  pinMode(6,INPUT);
  
  pinMode(8,INPUT);
  pinMode(9,INPUT);
  pinMode(10,INPUT);
  pinMode(11,INPUT);
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
  PCMSK0 |= (1 << PCINT0) | (1 << PCINT1) | (1 << PCINT2) | (1 << PCINT3);
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
  
  if ((1 << PCINT2) & checkState)
  {
    //Encoder 3(10 and 5)
    checkVal = digitalRead(5);
    if (digitalRead(10))//pulse high
    {
      if (checkVal)
      {
        enc3++;
      }
      else
      {
        enc3--;
      }
    }
    else//Opposite direction...
    {
      if (checkVal)
      {
        enc3--;
      }
      else
      {
        enc3++;
      }
    }
  }
  
  if ((1 << PCINT3) & checkState)
  {
    //Encoder 4(11 and 6)
    checkVal = digitalRead(6);
    if (digitalRead(11))//pulse high
    {
      if (checkVal)
      {
        enc4++;
      }
      else
      {
        enc4--;
      }
    }
    else//Opposite direction...
    {
      if (checkVal)
      {
        enc4--;
      }
      else
      {
        enc4++;
      }
    }
  }
  //update the previous value.
  prevPinState = pinState;
}


void loop()
{
  //wait for 100 ms
  delay(100);
  //print our current pin state (detected only through interrupts)
  cli();//Turn off interrupts right now. Safely fetch the pinstate value.
  e1 = enc1;
  e2 = enc2;
  e3 = enc3;
  e4 = enc4;
  sei();//Turn interrupts back on.
  
  Serial.println(e1);
}
