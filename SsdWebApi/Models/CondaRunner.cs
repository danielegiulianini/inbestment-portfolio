using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;


public class CondaRunner
{
    // strings collecting output/error messages, in case
    public StringBuilder _outputBuilder;        // private StringBuilder _errorBuilder;

    // The Python interpreter ('python.exe') that is used by this instance.
    public string CondaPath { get; }

    // The timeout for the underlying component in msec.
    public int Timeout { get; set; }

    // The anaconda environment to activate
    public string Environment { get; set; }

    // <param name="interpreter"> Full path to the Python interpreter ('python.exe').
    // <param name="timeout"> The script timeout in msec. Defaults to 10000 (10 sec).
    public CondaRunner(string condaPath, string environment, int timeout = 10000)
    {
        if (condaPath == null)
        {
            throw new ArgumentNullException(nameof(condaPath));
        }

        if (!File.Exists(condaPath))
        {
            throw new FileNotFoundException(condaPath);
        }

        CondaPath = condaPath;
        Timeout = timeout;
        Environment = environment;
    }

    // to run a sequence of dos commands, not read from a file
    public async Task<string> runPythonCommand(string pythonCommand)
    {
        _outputBuilder = new StringBuilder();
        string res = "";

        var processInfo = new ProcessStartInfo
        {
            // Separated FileName and Arguments
            FileName = "cmd.exe",
            Arguments = $"/c {CondaPath} activate {Environment}&&python {pythonCommand}",
            UseShellExecute = false,
            CreateNoWindow = false,
            ErrorDialog = false,
            RedirectStandardError = true,
            RedirectStandardOutput = true,
            RedirectStandardInput = true,
        };

        using (var process = new Process()
        {
            StartInfo = processInfo,   //enabling specified behaviour
            EnableRaisingEvents = true
        })
        {
            //add by me for error showing
            process.ErrorDataReceived += (sender, args) =>
            {
                string message = args.Data;

                if (message != null && message.StartsWith("Error"))
                {
                    // The vsinstr.exe process reported an error
                    _outputBuilder.AppendLine(message);
                }
            };

            process.OutputDataReceived += (sender, e) =>
            {
                // could be null terminated, needs null handling
                if (e.Data != null)
                {
                    Console.WriteLine("> " + e.Data);
                    _outputBuilder.AppendLine(e.Data);
                }
            };

            process.Exited += (sender, e) =>
            {
                // when Exited is called, OutputDataReceived could still being loaded
                // you need a proper release code here
                Console.WriteLine("exiting ...");
                res = _outputBuilder.ToString();
            };

            process.Start();

            // You need to call this explicitly after Start
            process.BeginOutputReadLine();
            
            process.BeginErrorReadLine(); //add by me for error showing

            // With WaitForExit, it is same as synchronous,
            // to make it truly asynchronous, you'll need to work on it from here
            await process.WaitForExitAsync();
        }

        return res;
    }
}