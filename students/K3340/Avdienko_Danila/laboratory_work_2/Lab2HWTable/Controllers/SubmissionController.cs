using System.Security.Claims;
using Lab2HWTable.Data;
using Lab2HWTable.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace Lab2HWTable.Controllers;

[Authorize] // только для зареганных и вошедших пользователей
public class SubmissionController : Controller
{
    private readonly AppDbContext _context;
    public SubmissionController(AppDbContext context)
    {
        _context = context;
    }

    [HttpGet]
    public IActionResult Create(int id)
    {
        return View(id); // передаем id дз
    }

    [HttpPost]
    public async Task<IActionResult> Create(int homeworkId, string answer)
    {
        var submission = new Submission
        {
            HomeworkId = homeworkId,
            StudentId = User.FindFirstValue(ClaimTypes.NameIdentifier)!, // id текущего пользователя
            Answer = answer
        };

        _context.Submissions.Add(submission);
        await _context.SaveChangesAsync();

        return RedirectToAction("Index", "Homework");
    }
}