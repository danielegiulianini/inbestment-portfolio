using System;
using System.Threading.Tasks;



namespace SsdWebApi.Models
{
    ///summary
    ///This class encapsulates python call to optimizer. 
    ///Call to ComputeOptimumPortfolio returns the optimal portfolio assets composition 
    ///in percentage.
    ///</summary>
    public class Optimization
    {
        private CondaRunner _CondaRunner;
   
         public Optimization(CondaRunner _CondaRunner){
            this._CondaRunner =_CondaRunner;
        }

        public async Task<string> ComputeOptimumPortfolio(Persistence P, Forecast F) //or return json object see it later
        {
            string[] indexIds = new string[] { "S&P_500_INDEX", "FTSE_MIB_INDEX", "GOLD_SPOT_$_OZ", "MSCI_EM", "MSCI_EURO", "All_Bonds_TR", "U.S._Treasury" };
            string res = "";

            //write indexes data to disk before call to optimizer as it will be fed to it
            foreach (var indexId in indexIds)
            {
                await P.ReadAndWriteIndexDataToCsvFile(indexId);
            }

            /*quoted are needed for preventing cmd from activating intepreter
            (indexIds contain special characters)*/
            string command = $"Models/python/get_optimum_portfolio.py";

            /*try is necessary in c# since it has'nt checked exceptions so there could be
            exceptions even if compiler doesn't require the programmer to catch them)*/
            try
            {
                string optimum_portfolio = await _CondaRunner.runPythonCommand(command);

                Console.WriteLine("from get_optimum_portfolio");

                if (string.IsNullOrWhiteSpace(optimum_portfolio))
                {
                    Console.WriteLine("Error in the script call or empty output");
                    goto lend;
                }

                res = optimum_portfolio;
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