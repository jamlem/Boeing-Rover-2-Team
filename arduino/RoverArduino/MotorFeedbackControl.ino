//This file focuses on the PID loop for the motors.
//Jeremy Lim

const byte pwmPinLeft = 0;
const byte pwmPinRight = 0;

float P = 1.0;
float I = 1.0;
float D = 0.0;//Derivative is zero for now.

//Integral accumulators for left and right motors.
float accumulateLeft = 0.0;
float accumulateRight = 0.0;

//Previous error values for left and right; for derivative term
float prevErrorLeft = 0.0;
float prevErrorRight = 0.0;

float ticksToCm = 1.0;//Convert encoder ticks to cm movement.
                      //arbitrary value for now.
                      

                    
//period is the amount of time since we last called
//This function (for velocity calculation)
void updateMotorSpeeds(double period)
{
  //Read our encoder values, and reset the variable that hold them.
  long encoderRight;
  long encoderLeft;
  cli();//Turn off interrupts right now. Safely fetch the pinstate value.
  e1 = encoderRight;
  e2 = encoderLeft;
  //reset to zero. Prevents overflow and allows for easy difference calculation.
  e1 = 0;
  e2 = 0;
  sei();//Turn interrupts back on.
  
  //Update 
}

//update our pwm output to the motor controller, via PWM.
void updateMotorCommands(double left, double right)
{
  
}
