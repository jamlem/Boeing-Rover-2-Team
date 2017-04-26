using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.VisualBasic;
using Renci.SshNet;
using System.Threading;
using Microsoft.Xna.Framework;
using System.Net;
using System.Net.Sockets;
using Microsoft.Xna.Framework.Input;
using System.IO;
using System.Diagnostics;
using Newtonsoft.Json;
using System.IO.Pipes;

namespace MarsRoverClient
{
    public partial class Form1 : Form
    {
        public SshClient sshClient = null;
        public bool isLan;
        public bool devicePowerStatus = true;
        public bool xboxControllerConnected;
        public bool xboxControllerState;
        public bool cameraFeed = false;
        public float postionX;
        public float positionY;
        public bool hopperDown = false;
        public bool hopperGrasp = false;
        public bool eStop = false;
        public bool allStop = false;
        public bool returnHome = false;
        public long pCMD;
        /// /////////////////////////////////////////////////////////////////////
        public float[] steeringValues;
        public float[] velocityValues;
        public int steeringValuesLength;
        public int velocityValuesLength;
        public int keepTrack = 0;
        IOHandler IO1 = new IOHandler();
        /// //////////////////////////////////////////////////////////////////////////
        public TcpClient clientSocket = new TcpClient();

        public int id;
        SshClient client = null;
        Process cmdPrompt = new Process();
        public sshHandlerClass sshHandlerConnection = new sshHandlerClass();
        public NamedPipeServerStream pipeServ = new NamedPipeServerStream("cameraFeed");

        public string dataConnectionIP;
        public int dataConnectionPort;
        public string cameraConnectionIP;
        public int cameraConnectionPort;

        public Thread dataTransferThread;
        

        public Form1(SshClient sshClient,bool isLanParam,string dataConnectionIPParam,int dataConnectionPortParam,string cameraConnectionIPParam,int cameraConnectionPortParam)
        {
            InitializeComponent();

            this.isLan = isLanParam;

            client = sshClient;
            dataConnectionIP = dataConnectionIPParam;
            dataConnectionPort = dataConnectionPortParam;
            cameraConnectionIP = cameraConnectionIPParam;
            cameraConnectionPort = cameraConnectionPortParam;
            id = (int)panel1.Handle;
            cameraFeedWAN.WorkerSupportsCancellation = true;
            cameraFeedWanConfiguration.WorkerSupportsCancellation = true;

            Thread xboxControllerIsConnected = new Thread(checkIsConnected);
            dataTransferThread = new Thread(dataTransfer);
            Thread xboxControllerButtonState = new Thread(CheckXBoxControllerButtonState);

            establishDataConnection();
            xboxControllerIsConnected.Start();
            xboxControllerButtonState.Start();

            //rchConsoleView.AppendText(" >> " + "Awaiting connection");

           

             
        }

        public void establishDataConnection()
        {
            try
            {
                clientSocket = new TcpClient();
                clientSocket.Connect(dataConnectionIP, dataConnectionPort);
            
                if((dataTransferThread.ThreadState == System.Threading.ThreadState.Suspended))
                {
                    dataTransferThread.Resume();
                }
                else
                {
                    dataTransferThread.Start();
                }
            }
            catch (Exception)
            {

                throw;
            }
                

           

                //MessageBox.Show("No data connection could be made");
                //dataConnectionMenuItemStringInvoke("Re-connect data transfer connection");
       
        }

        public void dataTransfer()
        {
            
            consoleTextInvoke(">> rover input data transfered \n");
            while (clientSocket.Connected)
            {

                try
                {
                    if (useControllerToolStripMenuItem.Checked)
                    {
                        CheckXBoxControllerButtonState();
                    }

                    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                    RoverInput roverInputData = new RoverInput();
                    if (returnHome)
                    {
                        
                        roverInputData = new RoverInput(steeringValues[keepTrack], velocityValues[keepTrack], eStop, allStop, hopperDown, hopperGrasp);
                        keepTrack--;
                    }
                    else
                    {
                        roverInputData = new RoverInput(postionX, positionY, eStop, allStop, hopperDown, hopperGrasp);
                        IO1.WriteData(string.Format("{0},{1}", roverInputData.MovementX * -1, roverInputData.MovementY * -1), "Tracking.txt");
                    }
                    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                    NetworkStream ns = clientSocket.GetStream();


                    byte[] jsonReciveBytes = new byte[clientSocket.ReceiveBufferSize];
                    ns.Read(jsonReciveBytes, 0, jsonReciveBytes.Length);
                    var rawStatus = Encoding.UTF8.GetString(jsonReciveBytes, 0, jsonReciveBytes.Length);
                    RoverStatus roverFeedbackData = JsonConvert.DeserializeObject<RoverStatus>(rawStatus);
                    roverFeedbackInvoke(roverFeedbackData.battery_volt, roverFeedbackData.heading, roverFeedbackData.ir_elevation, roverFeedbackData.ir_heading, roverFeedbackData.is_valid, roverFeedbackData.left_velocity, roverFeedbackData.right_velocity, roverFeedbackData.x_pos, roverFeedbackData.y_pos);

                    byte[] jsonSendBytes = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(roverInputData));
                    ns.Write(jsonSendBytes, 0, jsonSendBytes.Length);



                    if(disconnectDeviceToolStripMenuItem.Text == "Re-connect data transfer connection")
                    {
                        dataConnectionMenuItemStringInvoke("Disconnect data transfer connection");
                    }




                }
                catch (Exception e)
                {

                    MessageBox.Show("Data connection lost,please re-connect");
                    dataConnectionMenuItemStringInvoke("Re-connect data transfer connection");
                    clientSocket.Close();
                    clientSocket = null;
                    dataTransferThread.Suspend();
                    break;
                }


            }
        }

        public void checkIsConnected()
        {
            while (true)
            {
                if (xboxControllerClass.isXboxControllerConnected() != xboxControllerState)
                {

                    if (xboxControllerClass.isXboxControllerConnected())
                    {
                        xboxControllerConnected = true;
                        xboxControllerState = true;
                        useControllerToolStripMenuItem.Enabled = true;
                        xboxTextInvoke("    Connected");


                    }
                    else
                    {
                        xboxControllerConnected = false;
                        xboxControllerState = false;
                        useControllerToolStripMenuItem.Enabled = false;
                        useKeyboardToolStripMenuItem.Checked = true;
                        xboxTextInvoke("    Disconnected");

                    }
                }
            }


        }

        
        public void roverFeedbackInvoke(float voltage,float heading,float ir_evelation,float ir_heading,bool isValid,float leftVelo,float rightVelo,float xPos,float yPos)
        {
            if (InvokeRequired)
            {
                this.Invoke(new Action<float,float,float,float,bool,float,float,float,float>(roverFeedbackInvoke), voltage,heading,ir_evelation,ir_heading,isValid,leftVelo,rightVelo,xPos,yPos);
            }
            else
            {
                lblVoltage.Text = voltage.ToString();
                lblHeading.Text = heading.ToString();
                lblIREvelation.Text = ir_evelation.ToString();
                lblIRHeading.Text = ir_heading.ToString();
                lblIsOpen.Text = isValid.ToString();
                lblLeftVelo.Text = leftVelo.ToString();
                lblRightVelo.Text = rightVelo.ToString();
                lblXPos.Text = xPos.ToString();
                lblYPos.Text = yPos.ToString();
            }



        }

        public void xboxTextInvoke(string input)
        {
            if (InvokeRequired)
            {
                this.Invoke(new Action<string>(xboxTextInvoke), input);
            }
            else
            {
                xboxConnectionStrip.Text = input;
            }



        }

        public void dataConnectionMenuItemStringInvoke(string input)
        {
            if (InvokeRequired)
            {
                this.Invoke(new Action<string>(dataConnectionMenuItemStringInvoke), input);
            }
            else
            {
                disconnectDeviceToolStripMenuItem.Text = input;
            }



        }

        public void consoleTextInvoke(string input)
        {
            try
            {
                if (InvokeRequired)
                {
                    this.Invoke(new Action<string>(consoleTextInvoke), input);
                }
                else
                {
                    rchConsoleView.AppendText(input);
                }
            }
            catch (Exception)
            {

                MessageBox.Show("An Error has occured, please restart the client");
                Environment.Exit(0);
            }



        }

        public void CheckXBoxControllerButtonState()
        {
            bool movingState = false;

                if (useControllerToolStripMenuItem.Checked)
                {
                    GamePadState currentState = GamePad.GetState(PlayerIndex.One);

                    if (currentState.IsConnected && currentState.ThumbSticks.Left.Y != 0f || currentState.ThumbSticks.Left.X != 0f)
                    {
                        
                        consoleTextInvoke("Y: " + Math.Round(currentState.ThumbSticks.Left.Y, 2) + " , X: " + Math.Round(currentState.ThumbSticks.Left.X, 2) + "\n");
                        positionY = currentState.ThumbSticks.Left.Y;
                        postionX = currentState.ThumbSticks.Left.X;
                        movingState = true;
                    }

                if (currentState.IsConnected && currentState.Buttons.A == Microsoft.Xna.Framework.Input.ButtonState.Pressed)
                {
                    if (hopperDown)
                    {
                        hopperDown = false;
                    }
                    else
                    {
                        hopperDown = true;
                    }
                }

                if (currentState.IsConnected && currentState.Buttons.B == Microsoft.Xna.Framework.Input.ButtonState.Pressed)
                {
                    if (hopperGrasp)
                    {
                        hopperGrasp = false;
                    }
                    else
                    {
                        hopperGrasp = true;
                    }
                }

                if (currentState.IsConnected && currentState.Buttons.Y == Microsoft.Xna.Framework.Input.ButtonState.Pressed)
                {
                    if (eStop)
                    {
                        eStop = false;
                    }
                    else
                    {
                        eStop = true;
                    }
                }


                //if (currentState.IsConnected && currentState.ThumbSticks.Left.Y == 0f && currentState.ThumbSticks.Left.X == 0f && movingState == true)
                //{
                //    consoleTextInvoke("stopped");
                //    consoleTextInvoke("\n Postion Y: " + positionY + " , Position X: " + postionX);
                //    movingState = false;
                //}
            }
            
        }


        private void connectToControllerToolStripMenuItem_Click(object sender, EventArgs e)
        {
            useControllerToolStripMenuItem.Checked = false;
            useKeyboardToolStripMenuItem.Checked = true;
        }

        private void connectToRoverToolStripMenuItem_Click(object sender, EventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (client.IsConnected)
            {

                StringBuilder userInput = new StringBuilder();

                userInput.Append(txtCustomCommand.Text);
                using (var cmd = client.CreateCommand(userInput.ToString()))
                {
                    if (userInput.ToString() == "exit")
                    {
                        sshClient.Disconnect();
                        Console.WriteLine("Client Discounnected");

                    }
                    else
                    {
                        var results = cmd.Execute();
                        

                        rchConsoleView.AppendText(results);

                        
                    }
                }
                userInput.Clear();


            }
        }

        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Environment.Exit(0);
        }

        private void txtCustomCommand_KeyPress(object sender, KeyPressEventArgs e)
        {

        }

        private void txtCustomCommand_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == System.Windows.Forms.Keys.Enter)
            {
                button1_Click(this, new EventArgs());
            }
        }

        private void txtCustomCommand_TextChanged(object sender, EventArgs e)
        {

        }

        private void menuStrip1_KeyDown(object sender, KeyEventArgs e)
        {

        }


        public void MovementScript(string movementDirection)
        {
            if (client.IsConnected)
            {
                StringBuilder userInput = new StringBuilder();
                userInput.Append(movementDirection);
                using (var cmd = sshClient.CreateCommand(userInput.ToString()))
                {
                    var results = cmd.Execute();
                    rchConsoleView.AppendText(results);
                }
                userInput.Clear();
            }
        }

        private void Form1_KeyDown(object sender, KeyEventArgs e)
        {

            if (useKeyboardToolStripMenuItem.Checked)
            {
                if (e.KeyCode == System.Windows.Forms.Keys.W)
                {
                    positionY = 1;
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.S)
                {
                    positionY = -1;
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.A)
                {
                    postionX = -1;
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.D)
                {
                    postionX = 1;
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.Space)
                {
                    if (eStop)
                    {
                        eStop = false;
                    }
                    else
                    {
                        eStop = true;
                    }
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.V)
                {
                    if (hopperDown)
                    {
                        hopperDown = false;
                    }
                    else
                    {
                        hopperDown = true;
                    }
                    
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.B)
                {
                    if (hopperGrasp)
                    {
                        hopperGrasp = false;
                    }
                    else
                    {
                        hopperGrasp = true;
                    }
                }
            }

        }

        private void Form1_KeyUp(object sender, KeyEventArgs e)
        {
            if (useKeyboardToolStripMenuItem.Checked)
            {
                if (e.KeyCode == System.Windows.Forms.Keys.W)
                {
                    positionY = 0;
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.S)
                {
                    positionY = 0;
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.A)
                {
                    postionX = 0;
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.D)
                {
                    postionX = 0;
                }
                //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                else if (e.KeyCode == System.Windows.Forms.Keys.H)
                {
                    returnHome = true;
                    List<string> myrecords = new List<string>();
                    myrecords = IO1.ReadData("Tracking.txt");
                    int count = 0;
                    foreach (string item in myrecords)
                    {
                        string[] vals = item.Split(',');
                        steeringValues[count] = float.Parse(vals[0]);
                        velocityValues[count] = float.Parse(vals[1]);
                        count++;
                    }
                    steeringValuesLength = steeringValues.Length - 1;
                    velocityValuesLength = velocityValues.Length - 1;

                    keepTrack = steeringValuesLength;
                }
                else if (e.KeyCode == System.Windows.Forms.Keys.J)
                {
                    returnHome = false;
                }
                //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
            }
        }

        private void pictureBox1_Click(object sender, EventArgs e)
        {
            if (devicePowerStatus)
            {
                pictureBox1.Image = Properties.Resources.OffSwitch;
                devicePowerStatus = false;
            }
            else
            {
                pictureBox1.Image = Properties.Resources.OnSwicth;
                devicePowerStatus = true;
            }
        }

        private void pictureBox1_MouseHover(object sender, EventArgs e)
        {
            this.Cursor = Cursors.Hand;
        }

        private void pictureBox1_MouseLeave(object sender, EventArgs e)
        {
            this.Cursor = Cursors.Arrow;
        }

        private void toolStripStatusLabel1_Click(object sender, EventArgs e)
        {

        }

        private void devicesToolStripMenuItem_Click(object sender, EventArgs e)
        {

        }

        private void useControllerToolStripMenuItem_Click(object sender, EventArgs e)
        {
            useControllerToolStripMenuItem.Checked = true;
            useKeyboardToolStripMenuItem.Checked = false;
        }

        private void button1_Click_1(object sender, EventArgs e)
        {
            if(cameraFeed == false && isLan == true)
            {
                cameraFeedLAN.RunWorkerAsync();
                button1.Text = "Stop camera feed";
                cameraFeed = true;

            }
            else if (cameraFeed == true && isLan == true)
            {
                //cmdPrompt.CloseMainWindow();
                sshHandlerConnection.LANCameraConnectionKill(client, id);
                button1.Text = "Start camera feed";
                cameraFeed = false;
            }
            else if (cameraFeed == false && isLan == false)
            {
                //cmdPrompt.CloseMainWindow();

               
                if (cameraFeedWAN.IsBusy)
                {
                    cameraFeedWanConfiguration.CancelAsync();
                    cameraFeedWAN.CancelAsync();
                }
                else
                {
                    cameraFeedWAN.RunWorkerAsync();
                    cameraFeedWanConfiguration.RunWorkerAsync();
                }

                

                button1.Text = "Stop camera feed";
                cameraFeed = true;
            }
            else if (cameraFeed == true && isLan == false)
            {
                //cmdPrompt.CloseMainWindow();
                //backgroundWorker2.CancelAsync();
                sshHandlerConnection.WANCameraConnectionKill();
                if (cameraFeedWAN.IsBusy || cameraFeedWanConfiguration.IsBusy)
                {
                    cameraFeedWanConfiguration.CancelAsync();
                    cameraFeedWAN.CancelAsync();
                }
                else
                {
                    cameraFeedWAN.RunWorkerAsync();
                    cameraFeedWanConfiguration.RunWorkerAsync();
                }
                button1.Text = "Start camera feed";
                cameraFeed = false;
            }





        }

        private void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
        {

            if (client.IsConnected)
            {

               sshHandlerConnection.LANCameraConnection(client, id);

            }
            else
            {
                MessageBox.Show("No connection to the rover made");

            }
        }



        private void disconnectDeviceToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (clientSocket == null || (!(clientSocket.Connected)))
            {
                establishDataConnection();
            }
            else
            {
                if (clientSocket.Connected)
                {
                    clientSocket.Close();
                    dataConnectionMenuItemStringInvoke("Re-connect data transfer connection");
                    dataTransferThread.Suspend();
                }
                
            }
        }

        private void backgroundWorker2_DoWork(object sender, DoWorkEventArgs e)
        {
            try
            {
                Thread.Sleep(500);
                sshHandlerConnection.WANCameraConnection(client, "cameraFeed", id);
                pipeServ.WaitForConnection(); 
                StreamWriter sw = new StreamWriter(pipeServ);
                sw.AutoFlush = true;

                TcpClient tcpCamera = new TcpClient();
                tcpCamera.Connect(cameraConnectionIP, cameraConnectionPort); /// web crawler for it
                NetworkStream camStream = tcpCamera.GetStream();

                int read = 0;
                byte[] bytes = new byte[tcpCamera.ReceiveBufferSize];
                while (tcpCamera.Connected)
                {
                    read = camStream.Read(bytes, 0, tcpCamera.ReceiveBufferSize);
                    if (read > 0)
                        pipeServ.Write(bytes, 0, read);
                }
            }
            catch (IOException ex)
            {
                MessageBox.Show(ex.Message);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void label11_Click(object sender, EventArgs e)
        {

        }

        private void cameraFeedWAN_DoWork(object sender, DoWorkEventArgs e)
        {
            StringBuilder userInput = new StringBuilder();

            userInput.Append("raspivid -w 200 -h 150 -t 9999999 --framerate 10 -o - | nc -l 5888");
            //raspivid -vf -n -w 800 -h 400 -o - -t 0 -b 2000000 | nc -l 5888
            //raspivid--width 600--height 400 - t 9999999--framerate 25--output - | nc - l 5556
            using (var cmd = client.CreateCommand(userInput.ToString()))
            {



                cmd.Execute();


                //rchConsoleView.AppendText(results);
            }
        }

        private void Form1_KeyPress(object sender, KeyPressEventArgs e)
        {

        }

        private void button2_Click(object sender, EventArgs e)
        {
            
        }
    }
}
