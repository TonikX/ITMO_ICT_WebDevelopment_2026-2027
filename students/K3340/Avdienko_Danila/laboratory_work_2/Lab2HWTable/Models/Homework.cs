namespace Lab2HWTable.Models;

public class Homework
{
    public int Id { get; set; }
    public string Subject { get; set; } = string.Empty;
    public string Teacher { get; set; } = string.Empty;
    public DateTime IssueDate { get; set; }
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public string Description { get; set; } = string.Empty;
    public string PenaltyInfo { get; set; } = string.Empty;
}