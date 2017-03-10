
// this class specifically will be sent to the rover every 0.2 seconds with updated values that will be relayed to the arduino
//bellow is an example of what is the output after JSON object is deserialised ince sent to the raspberry pi

//{
//  "MovementX": 100.0,
//  "MovementY": 100.0,
//  "EStopSwitch": true,
//  "HopperUpStatus": true
//}


using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace JSON_TEST
{
    public class RoverInput
    {

        #region properties
        private float movementX;
        private float movementY;
        private bool eStopSwitch;
        private bool hopperUpStatus;
        #endregion


        #region Fields

        public float MovementX
        {
            get
            {
                return movementX;
            }

            set
            {
                movementX = value;
            }
        }

        public float MovementY
        {
            get
            {
                return movementY;
            }

            set
            {
                movementY = value;
            }
        }

        public bool EStopSwitch
        {
            get
            {
                return eStopSwitch;
            }

            set
            {
                eStopSwitch = value;
            }
        }

        public bool HopperUpStatus
        {
            get
            {
                return hopperUpStatus;
            }

            set
            {
                hopperUpStatus = value;
            }
        }

        #endregion

        #region Constructors and Methods

        public RoverInput(float movementXParam,float movementYParam,bool eStopSwitchParam,bool hopperUpStatusParam)
        {
            this.movementX = movementXParam;
            this.movementY = movementYParam;
            this.eStopSwitch = eStopSwitchParam;
            this.hopperUpStatus = hopperUpStatusParam;
        }

        public RoverInput()
        {

        }

        #endregion


    }
}
