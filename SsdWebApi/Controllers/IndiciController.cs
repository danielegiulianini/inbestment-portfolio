using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using SsdWebApi.Models;
using Microsoft.Extensions.Configuration;



namespace SsdWebApi.Controllers
{
    [ApiController]
    [Route("api/indici")]
    public class IndiciController : ControllerBase
    {
        private readonly IndiciContext _context;
        private readonly Persistence P;
        private readonly Optimization O;
        private readonly Forecast F;
        public IndiciController(IndiciContext context, IConfiguration configuration)
        {
            _context = context;

            string condaPath = configuration["condaPath"];
            string environment  = configuration["environment"];
            int timeout = 10000; 
            CondaRunner _CondaRunner = new CondaRunner(condaPath, environment, timeout);

            F = new Forecast(_CondaRunner);
            O = new Optimization(_CondaRunner);
            P = new Persistence(context);
        }

        [HttpGet]
        public ActionResult<List<Indici>> GetAll() => _context.indici.ToList();


        [HttpGet("{indexIdByClient}")]
        public async Task<string> GetIndexForecast(int indexIdByClient)
        {
            //simple validation
            string[] indicesIds = new string[] { "S&P_500_INDEX", "FTSE_MIB_INDEX", "GOLD_SPOT_$_OZ", "MSCI_EM", "MSCI_EURO", "All_Bonds_TR", "U.S._Treasury" };
            if (indexIdByClient > indicesIds.Length - 1) 
            {
                indexIdByClient = indicesIds.Length - 1;
            } else 
            {
                if (indexIdByClient < 0) {
                    indexIdByClient = 0;
                }
            }

            await P.ReadAndWriteIndexDataToCsvFile(indicesIds[indexIdByClient]);
            return await F.forecast(indicesIds[indexIdByClient]);            //return json forecast
        }

        
        [HttpGet("portfolio")]
        public async Task<string> GetPortfolio() => await O.ComputeOptimumPortfolio(P, F);

    }
}