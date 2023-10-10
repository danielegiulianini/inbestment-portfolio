using System;
using System.Threading.Tasks;


namespace SsdWebApi.Models
{

    ///<summary>
    ///This class encapsulates python call for forecasting future time series data values 
    ///of a single asset. Call to forecast method returns the forecasted textual and graphical 
    ///(as a plot) values as json together with some accuracy measures and the model used.
    ///</summary>

    public class Forecast
    {
        private CondaRunner _CondaRunner;
        public Forecast(CondaRunner _CondaRunner){
            this._CondaRunner = _CondaRunner;
        }

        public async Task<string> forecast(string indexId)
        {
            string res = "";

            /*quoted are needed for preventing cmd from activating intepreter
            (indexIds contain special characters)*/
            string command = $"Models/python/forecast_arima.py \"{indexId}.csv\"";

            /*try is nedded in c# since it has not checked exceptions (so there could be 
            exceptions even if compiler doesn't require the programmer to catch them)*/
            try
            {
                string forecastedSeriesJson = await _CondaRunner.runPythonCommand(command);

                Console.WriteLine("from forecast");

                if (string.IsNullOrWhiteSpace(forecastedSeriesJson))
                {
                    Console.WriteLine("Error in the script call or empty output");
                    goto lend;
                }

                res = forecastedSeriesJson;
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                goto lend;
            }


        lend: return res;
        }
    }
}





