using Lab2HWTable.Data;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Lab2HWTable.Controllers;

public class HomeworkController : Controller
{
    private readonly AppDbContext _context;

    public HomeworkController(AppDbContext context)
    {
        _context = context;
    }
    public IActionResult Index(string? search, string? teacher, int page = 1)
    {
        var homeworks = _context.Homeworks.AsQueryable();

        ViewBag.Teachers = _context.Homeworks
            .Select(h => h.Teacher)
            .Distinct()
            .ToList();

        if (!string.IsNullOrEmpty(search))
            homeworks = homeworks.Where(h => h.Subject.Contains(search));

        if (!string.IsNullOrEmpty(teacher))
            homeworks = homeworks.Where(h => h.Teacher == teacher);

        int pageSize = 5;

        if (page < 1)
            page = 1;

        ViewBag.Page = page;
        ViewBag.TotalPages = (int)Math.Ceiling(homeworks.Count() / (double)pageSize);
        ViewBag.Search = search;
        ViewBag.Teacher = teacher;

        var result = homeworks
            .OrderBy(h => h.Id)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToList();

        return View(result);
    }
    
    public IActionResult Grades()
    {
        var submissions = _context.Submissions
            .Include(s => s.Homework)
            .ToList(); // получаем сданные работы вместе с заданиями

        ViewBag.Students = _context.Users
            .Where(u => u.Email != "teacher@gmail.com")
            .ToDictionary(u => u.Id, u => u.Email); // получаем почту учеников по адйи
        
        ViewBag.Subjects = _context.Homeworks
            .Select(h => h.Subject)
            .Distinct()
            .ToList(); // все предметы без повторений
        return View(submissions);
    }
}