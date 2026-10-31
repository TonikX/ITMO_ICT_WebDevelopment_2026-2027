using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace Lab2HWTable.Controllers;

public class AccountController : Controller
{
    private readonly UserManager<IdentityUser> _userManager; // создание пользователей и работа с их данными
    private readonly SignInManager<IdentityUser> _signInManager; // вход пользователей в систему

    public AccountController(UserManager<IdentityUser> userManager, SignInManager<IdentityUser> signInManager)
    {
        _userManager = userManager;
        _signInManager = signInManager;
    }

    [HttpGet]
    public IActionResult Register()
    {
        return View(); // возвращаем страницу регистрации, когда гет запрос на нее
    }

    [HttpPost]
    public async Task<IActionResult> Register(string email, string password) // пост запрос, когда делаем юзера
    {
        var user = new IdentityUser
        {
            UserName = email, // имейл как юзернейм
            Email = email
        };

        // создаем пользователя в бд
        var result = await _userManager.CreateAsync(user, password);

        if (!result.Succeeded)
        {
            return View();
        }

        await _signInManager.SignInAsync(user, false);
        return RedirectToAction("Index", "Home");
    }
    
    [HttpGet]
    public IActionResult Login()
    {
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> Login(string email, string password)
    {
        var result = await _signInManager.PasswordSignInAsync(email, password, false, false);

        if (!result.Succeeded)
        {
            return View();
        }

        return RedirectToAction("Index", "Homework");
    }
    
    [HttpPost]
    public async Task<IActionResult> Logout()
    {
        await _signInManager.SignOutAsync(); // выходим из аккаунта
        return RedirectToAction("Login");
    }
}