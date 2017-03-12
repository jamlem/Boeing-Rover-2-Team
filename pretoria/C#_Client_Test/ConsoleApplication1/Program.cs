using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using Newtonsoft.Json;

namespace Client {
    public class SynchronousSocketClient
    {

        public static void StartClient()
        {
            byte[] bytes = new byte[4096];
            try
            {
                IPHostEntry ipHostInfo = Dns.Resolve(Dns.GetHostName());
                IPAddress ipAddress = ipHostInfo.AddressList[0];
                IPEndPoint remoteEP = new IPEndPoint(ipAddress, 5555);
                Socket sender = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                try
                {
                    sender.Connect(remoteEP);
                    Console.WriteLine("Socket connected to {0}", sender.RemoteEndPoint.ToString());
                    
                    byte[] msg = Encoding.UTF8.GetBytes(getJSONString());
                    int bytesSent = sender.Send(msg);
                    int bytesRec = sender.Receive(bytes);
                    var rawStatus = Encoding.UTF8.GetString(bytes, 0, bytesRec);
                    RoverStatus status = JsonConvert.DeserializeObject<RoverStatus>(rawStatus);
                    Console.WriteLine(status.ToString());
                    Console.ReadKey();
                    sender.Shutdown(SocketShutdown.Both);
                    sender.Close();

                }
                catch (ArgumentNullException ane)
                {
                    Console.WriteLine("ArgumentNullException : {0}", ane.ToString());
                }
                catch (SocketException se)
                {
                    Console.WriteLine("SocketException : {0}", se.ToString());
                }
                catch (Exception e)
                {
                    Console.WriteLine("Unexpected exception : {0}", e.ToString());
                }

            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }

        public static string getJSONString()
        {
            return JsonConvert.SerializeObject(new RoverInput(1, 1, false, false, false));
        }

        public static int Main(String[] args)
        {
            StartClient();
            return 0;
        }
    }
}
