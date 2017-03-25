//This file focuses on the PID loop for the motors.
//Jeremy Lim

const byte pwmPinLeft = 2;
const byte pwmPinRight = 3;

float P_const = 1.0;
float I_const = 1.0;
float D_const = 0.0;//Derivative is zero for now.

//Integral accumulators for left and right motors.
float accumulateLeft = 0.0;
float accumulateRight = 0.0;

//Previous error values for left and right; for derivative term
float prevErrorLeft = 0.0;
float prevErrorRight = 0.0;

float ticksToCm = 1.0;//Convert encoder ticks to cm movement.
                      //arbitrary value for now.
                      
float constrainMax = 127.0;//Maximum value of integral terms.
                    
//period is the amount of time since we last called
//This function (for velocity calculation)
void updateMotorSpeeds(double period)
{
  //Read our encoder values, and reset the variable that hold them.
  long encoderRight;
  long encoderLeft;
  cli();//Turn off interrupts right now. Safely fetch the pinstate value.
  encoderRight = e1;
  encoderLeft  = e2;
  //reset to zero. Prevents overflow and allows for easy difference calculation.
  e1 = 0;
  e2 = 0;
  sei();//Turn interrupts back on.
  
  //Update 
  velocityLeft =  encoderLeft*ticksToCm;
  velocityRight = encoderRight*ticksToCm;
}

//update our pwm output to the motor controller, via PWM.
void updateMotorCommands(double left, double right)
{
  //update our target speeds.
  //Global variables
  commandLeft = left;
  commandRight = right;
  
  float errorLeft =  velocityLeft - commandLeft;
  float errorRight = velocityRight - commandRight;
  
  float delErrorLeft = errorLeft - prevErrorLeft;
  float delErrorRight = errorRight - prevErrorRight;
  
  //Update the integral terms
  accumulateLeft += I_const*errorLeft;
  accumulateRight += I_const*errorRight;
  
  //Constrain to fight integral winding.
  accumulateLeft = constrain(accumulateLeft,-constrainMax,constrainMax);
  accumulateRight = constrain(accumulateRight,-constrainMax,constrainMax);
  
  //PID calculation
  float leftControl = errorLeft*P_const + accumulateLeft + D_const*delErrorLeft;
  float rightControl = errorRight*P_const + accumulateRight + D_const*delErrorRight;
  
  //Update values holding the previous error
  prevErrorLeft = errorLeft;
  prevErrorRight = errorRight;
  
  //write to pwm control: pins 2 and 3
  analogWrite(pwmPinLeft,leftControl);
  analogWrite(pwmPinRight,rightControl);
}
