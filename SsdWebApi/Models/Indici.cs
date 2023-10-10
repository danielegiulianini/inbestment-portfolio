using System.ComponentModel.DataAnnotations.Schema;

namespace SsdWebApi.Models
{
    [Table("serie storica indici")]
    public class Indici
    {
        [Column("PK_UID")]
        public int id { get; set; }
        [Column("Dates")]
        public string Data { get; set; }
        [Column("S&P_500_INDEX")]
        public double SP_500 { get; set; }
        [Column("FTSE_MIB_INDEX")]
        public double FTSE_MIB { get; set; }
        [Column("GOLD_SPOT_$_OZ")]
        public double GOLD_SPOT { get; set; }
        [Column("MSCI_EM")]
        public double MSCI_EM { get; set; }
        [Column("MSCI_EURO")]
        public double MSCI_EURO { get; set; }
        [Column("All_Bonds_TR")]
        public double All_Bonds { get; set; }
        [Column("U.S._Treasury")]
        public double US_Treasury { get; set; }
    }
}