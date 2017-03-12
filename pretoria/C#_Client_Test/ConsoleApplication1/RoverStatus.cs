using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace Client
{

    public class RoverStatus
    {
        public float battery_volt { get; set; }
        public float heading { get; set; }
        public float ir_elevation { get; set; }
        public float ir_heading { get; set; }
        public bool is_valid { get; set; }
        public float left_velocity { get; set; }
        public float right_velocity { get; set; }
        public float x_pos { get; set; }
        public float y_pos { get; set; }

        public RoverStatus(bool isValid, float battery_volt, float heading, float ir_elevation, float ir_heading, float left_velocity, float right_velocity, float x_pos, float y_pos)
        {
            this.is_valid = isValid;
            this.battery_volt = battery_volt;
            this.ir_elevation = ir_elevation;
            this.ir_heading = ir_heading;
            this.left_velocity = left_velocity;
            this.right_velocity = right_velocity;
            this.x_pos = x_pos;
            this.y_pos = y_pos;
        }

        public RoverStatus()
        {

        }

        public override string ToString()
        {
            return string.Format("Valid = {0}\nVolts = {1}\nIR Elevation = {2}\nIR Heading = {3}\nLeft Velocity = {4}\nRight Velocity = {5}\nX Pos = {6}\nY Pos = {7}", is_valid, battery_volt, ir_elevation, ir_heading, left_velocity, right_velocity, x_pos, y_pos);
        }
    }

}
