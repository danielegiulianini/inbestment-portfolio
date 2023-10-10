using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;
using System.IO;
using System.Threading.Tasks;

namespace SsdWebApi.Models
{
    
    ///<summary>
    ///Class containing some utilities for reading indexes time serie data from a sqlite
    ///database and converting it to a .csv file for python reading.
    ///</summary>
    public class Persistence
    {
        private IndiciContext _context;

        public Persistence(IndiciContext context)
        {
            _context = context;
        }

        ///<summary>
        ///Given its column name in original sqlite DB, it reads a single index from it and 
        ///returns a dictionary made of (Date, value) pairs.
        ///</summary>
        private async Task<Dictionary<string, string>> ReadIndexFromDb(string chosenIndex)
        {
            Dictionary<string, string> serie = new Dictionary<string, string>();
            using (var command = _context.Database.GetDbConnection().CreateCommand())     //must use ADO.NET because indexId comes as string
            {
                command.CommandText = $"SELECT \"Dates\", \"{chosenIndex}\" from \"serie storica indici\"";     //SQLite doesn't allow special characters in queries so quoting is compulsory
                await _context.Database.OpenConnectionAsync();
                using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        serie.Add(reader["Dates"].ToString(), reader[chosenIndex].ToString());
                    }
                }
            }

            return serie;
        }

        ///<summary>
        ///Given its column name in original sqlite DB, it reads a single index from it and 
        ///write it to a csv file made of dates and values info. 
        ///</summary>
        public async Task ReadAndWriteIndexDataToCsvFile(string chosenIndex)
        {
            string indexDataFileName = "Models/assets/" + chosenIndex + ".csv";
            string separator = ";";

            using (StreamWriter streamWriter = new StreamWriter(indexDataFileName, false))
            {
                await streamWriter.WriteLineAsync("Dates" + separator + chosenIndex);
                var indexes = await ReadIndexFromDb(chosenIndex);
                foreach (var element in indexes)
                {
                    await streamWriter.WriteLineAsync(element.Key + separator + element.Value);
                }
            }
        }

    }

}