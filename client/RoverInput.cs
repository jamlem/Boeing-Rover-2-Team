
// this class specifically will be sent to the rover every 0.2 seconds with updated values that will be relayed to the arduino
//bellow is an example of what is the output after JSON object is deserialised ince sent to the raspberry pi


//{
//  "MovementX": 100.0,
//  "MovementY": 100.0,
//  "EStopStatus": false,
//  "HopperGrasp": true,
//  "HopperDown": true
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
        private float movementX; //  value from 0 to 1 will be sent,angle will be detrmined by arduino
        private float movementY; // value from 0 to 1 will be sent,this will be multiplied by voltage to control speed
        private bool eStopStatus; // bool to check the eStopStatus, if true it means the rover is on, if not it means its off
        private bool hopperGrasp; // bool to check hopper arm grasp
        private bool hopperDown; // bool to check if the hopper is facing the floor, if true then it is, if false then its not
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

        public bool EStopStatus
        {
            get
            {
                return eStopStatus;
            }

            set
            {
                eStopStatus = value;
            }
        }

        public bool HopperGrasp
        {
            get
            {
                return hopperGrasp;
            }

            set
            {
                hopperGrasp = value;
            }
        }

        public bool HopperDown
        {
            get
            {
                return hopperDown;
            }

            set
            {
                hopperDown = value;
            }
        }

        #endregion

        #region Constructors and Methods

        public RoverInput(float movementXParam,float movementYParam,bool eStopStatusParam,bool hopperGraspParam,bool hopperDownParam)
        {
            this.movementX = movementXParam;
            this.movementY = movementYParam;
            this.eStopStatus = eStopStatusParam;
            this.hopperGrasp = hopperGraspParam;
            this.hopperDown = hopperDownParam;
        }

        public RoverInput()
        {

        }

        #endregion


    }
}
