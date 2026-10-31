using Lab2HWTable.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Lab2HWTable.Controllers;

[Authorize(Roles = "Teacher")] // доступ только роли тичер
public class TeacherController : Controller
{
    private readonly AppDbContext _context;

    public TeacherController(AppDbContext context)
    {
        _context = context;
    }

    [HttpGet]
    public IActionResult Index()
    {
        var submissions = _context.Submissions.Include(s => s.Homework).ToList();
        
        ViewBag.Students = _context.Users
            .ToDictionary(u => u.Id, u => u.Email); // получаем почты учеников по их id
        
        return View(submissions); // передаем все сданные работы на страницу
    }

    [HttpPost]
    public async Task<IActionResult> Grade(int id, int grade)
    {
        var submission = await _context.Submissions.FindAsync(id);
        if (submission == null)
            return NotFound();
        submission.Grade = grade; // ставим оценку
        await _context.SaveChangesAsync(); // сохраняем в бд

        return RedirectToAction("Index");
    }
}