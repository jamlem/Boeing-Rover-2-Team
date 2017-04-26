using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

namespace MarsRoverClient
{
    public class IOHandler
    {
        private FileStream streamer;
        private StreamReader reader;
        private StreamWriter writer;

        public void OverWriteData(string data, string filePath)
        {
            try
            {
                streamer = new FileStream(filePath, FileMode.Create, FileAccess.Write);
                writer = new StreamWriter(streamer);

            
                    writer.WriteLine(data);
                
            }
            catch (FileNotFoundException)
            {
                //System.Windows.Forms.MessageBox.Show("File not Found");
            }
            catch (DirectoryNotFoundException)
            {
                ///System.Windows.Forms.MessageBox.Show("Directory not Found");
            }
            catch (IOException)
            {
                //System.Windows.Forms.MessageBox.Show("An error has occured");
            }
            finally
            {
                writer.Close();
                streamer.Close();
            }
        }

        public List<string> ReadData(string filePath)
        {
            List<string> data = new List<string>();

            try
            {
                streamer = new FileStream(filePath, FileMode.Open, FileAccess.Read);
                // object list = formatter.Deserialize(streamer);
                reader = new StreamReader(streamer);

                while (!reader.EndOfStream)
                {
                    data.Add(reader.ReadLine());
                }
            }
            catch (FileNotFoundException)
            {
                //System.Windows.Forms.MessageBox.Show("File not Found");
            }
            catch (DirectoryNotFoundException)
            {
                //System.Windows.Forms.MessageBox.Show("Directory not Found");
            }
            catch (IOException)
            {
                //System.Windows.Forms.MessageBox.Show("An error has occured");
            }
            finally
            {
                reader.Close();
                streamer.Close();
            }

            return data;
        }
        /// //////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        public void WriteData(string data, string filePath)
        {
            try
            {
                streamer = new FileStream(filePath, FileMode.Append, FileAccess.Write);
                writer = new StreamWriter(streamer);


                writer.WriteLine(data);

            }
            catch (FileNotFoundException)
            {
                //System.Windows.Forms.MessageBox.Show("File not Found");
            }
            catch (DirectoryNotFoundException)
            {
                ///System.Windows.Forms.MessageBox.Show("Directory not Found");
            }
            catch (IOException)
            {
                //System.Windows.Forms.MessageBox.Show("An error has occured");
            }
            finally
            {
                writer.Close();
                streamer.Close();
            }
        }

        /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    }
}
