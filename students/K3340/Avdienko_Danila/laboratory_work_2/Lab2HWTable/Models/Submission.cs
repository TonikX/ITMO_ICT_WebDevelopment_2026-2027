namespace Lab2HWTable.Models;

public class Submission
{
    public int Id { get; set; }
    public int HomeworkId { get; set; }
    public Homework Homework { get; set; } = null!;
    public string StudentId { get; set; } = string.Empty;
    public string Answer { get; set; } = string.Empty;
    public int? Grade { get; set; }
}