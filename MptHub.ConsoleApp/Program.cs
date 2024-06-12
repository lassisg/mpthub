using System.Globalization;
using System.Text;
using CsvHelper;
using CsvHelper.Configuration;
using CsvHelper.Configuration.Attributes;
using MptHub.Domain;

// Add menu

// Load configurations
var generalConfig = new GeneralConfiguration();
var analysisConfig = new AnalysisConfiguration();
var diffusivityConfig = new DiffusivityConfiguration();

// Import csv
List<TrajectoryFile> result = [];
const string fileName = "D:/github/MPTHub/MptHub.ConsoleApp/561_D2_H2O_200ul_Series001_RAW_ch00.csv";

var configuration = new CsvConfiguration(CultureInfo.InvariantCulture)
{
    Encoding = Encoding.UTF8, // Our file uses UTF-8 encoding.
    Delimiter = ",", // The delimiter is a comma.
    
};

using (var reader = new StreamReader(fileName)) 
using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
{
    var records = csv.GetRecords<TrajectoryFile>();
    Console.ReadLine();
    // // result = records.ToList();
    // foreach (TrajFile item in records)
    // {
    //     Console.WriteLine($"Trajectory { item.Trajectory, 3 }, Frame { item.Frame, 3 }, ({ item.x }, { item.y })");
    // }
}

// Analyze (TrackPy motion)

// Export excel

Console.ReadLine();

// Update analysis config
// Update general config
// Update diffusivity config

public class TrajectoryFile
{
    [Index(1)]
    public int Trajectory { get; set; }
    [Index(2)]
    public int Frame { get; set; }
    [Index(3)]
    public double x { get; set; }
    [Index(4)]
    public double y { get; set; }
}