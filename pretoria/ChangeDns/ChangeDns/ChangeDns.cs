using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Xml;

namespace ChangeDns
{
    class ChangeDns 
    {
        public ChangeDns()
        {
            changeDns(getPublicIP());
        }
        public static void changeDns(string externalIP) //accesses web-based API to change dns server IP current public IP address
        {
            try
            {
                var URL = "https://www.dnsdynamic.org/api/?hostname=rover.pretoria.dnsdynamic.net&myip=" + externalIP; //http address of wanted server

                Console.WriteLine("Logging in...");
                var myCredentials = new NetworkCredential("vheerden.jason@gmail.com", "IncorDns456"); //creates service login details
                var myWebRequest = WebRequest.Create(URL); //formulates web request to dns server
                myWebRequest.Credentials = myCredentials; //set credentials for request
                Console.WriteLine("Getting Server Response...\n");
                var myWebResponse = myWebRequest.GetResponse(); //get respones from web service
                var responseStream = readResponse(myWebResponse); //reads response
                Console.WriteLine("-Server-");
                Console.WriteLine(responseStream); //shows server response. nochg means dns IP has not changed, nohost means incorrect hostname was specified, ok will mean service has been changed.
                myWebResponse.Close();
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }
        public static string getPublicIP()
        {
            try
            {
                Console.WriteLine("Getting external IP...");
                var externalIP = new WebClient().DownloadString(@"http://icanhazip.com").Trim(); //accesses website to get current public IP address
                Console.WriteLine("External IP: " + externalIP + "\n");
                return externalIP;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                return null;
            }
        }
        private static string readResponse(WebResponse wr)
        {
            using (var sr = new StreamReader(wr.GetResponseStream()))
            {
                return sr.ReadToEnd(); //converts webresponse into a readable string using a streamreader
            }
        }

    }

}
