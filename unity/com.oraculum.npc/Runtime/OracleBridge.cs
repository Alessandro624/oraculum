#if UNITY_EDITOR
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using UnityEditor.PackageManager;
using UnityEngine;

namespace Oraculum.Unity
{
    [Serializable]
    internal class Consult
    {
        public string question, formula;
        public int reverence;
    }

    internal sealed class OracleBridge : IDisposable
    {
        [Serializable]
        private class Reply { public bool ready; public string comment, error; }

        private Process process;
        private bool busy;

        public async Task<string> Ask(Consult request)
        {
            if (busy) throw new InvalidOperationException("A consultation is already in progress.");
            busy = true;
            try
            {
                if (process == null)
                {
                    var root = PackageInfo.FindForAssembly(typeof(OracleBridge).Assembly).resolvedPath;
                    bool windows = Application.platform == RuntimePlatform.WindowsEditor;
                    string path = Path.Combine(root, "Tools~", windows ? "Windows" : "Linux",
                        windows ? "oraculum-bridge.exe" : "oraculum-bridge");
                    var start = new ProcessStartInfo(path) {
                        UseShellExecute = false, CreateNoWindow = true,
                        RedirectStandardInput = true, RedirectStandardOutput = true,
                        StandardOutputEncoding = Encoding.UTF8
                    };
                    process = Process.Start(start);
                    var init = await Exchange(JsonUtility.ToJson(OracleSettings.Load()));
                    if (!init.ready) throw new IOException("The bridge is not ready.");
                }
                return (await Exchange(JsonUtility.ToJson(request))).comment;
            }
            catch { Dispose(); throw; }
            finally { busy = false; }
        }

        private async Task<Reply> Exchange(string json)
        {
            // Write UTF-8 explicitly, including on Windows with a legacy code page.
            byte[] bytes = Encoding.UTF8.GetBytes(json + "\n");
            await process.StandardInput.BaseStream.WriteAsync(bytes, 0, bytes.Length);
            await process.StandardInput.BaseStream.FlushAsync();
            var read = process.StandardOutput.ReadLineAsync();
            if (await Task.WhenAny(read, Task.Delay(90000)) != read)
                throw new TimeoutException("The oracle took more than 90 seconds to respond.");
            var line = await read;
            if (line == null) throw new IOException("The bridge closed the connection.");
            var reply = JsonUtility.FromJson<Reply>(line);
            if (!string.IsNullOrEmpty(reply.error)) throw new IOException(reply.error);
            return reply;
        }

        public void Dispose()
        {
            var child = process;
            process = null;
            if (child == null) return;
            try { child.StandardInput.Close(); }
            catch (InvalidOperationException) { }
            finally { child.Dispose(); }
        }
    }
}
#endif
