namespace MptHub.Domain;

// TODO: Implement generic for config? 
// TODO: Use configuration files? 
// TODO: Use .env files?
public interface IConfiguration
{
    public Dictionary<string, string> KeyValue { get; set; }
    public Dictionary<string, string> LoadConfiguration();
}