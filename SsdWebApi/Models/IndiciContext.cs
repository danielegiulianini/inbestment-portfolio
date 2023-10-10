using Microsoft.EntityFrameworkCore;



namespace SsdWebApi.Models
{
    public class IndiciContext : DbContext
    {
        public IndiciContext(DbContextOptions<IndiciContext> options)
        : base(options)
        {
        }

        public DbSet<Indici> indici { get; set; }
    }
}
