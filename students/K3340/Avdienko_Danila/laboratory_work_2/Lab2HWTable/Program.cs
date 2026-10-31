using Lab2HWTable.Data;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddDbContext<AppDbContext>(options => options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddControllersWithViews(); // подключаем контроллеры и представления

builder.Services.AddIdentity<IdentityUser, IdentityRole>()
    .AddEntityFrameworkStores<AppDbContext>(); // подключаем пользователей и роли через наш контекст

var app = builder.Build();
app.UseStaticFiles(); // для css
// мидлвейр для всех хттп запросов
app.UseRouting(); // определяем маршрут
app.UseAuthentication(); // определяем, кто вошёл в систему
app.UseAuthorization(); // проверяем права доступа

app.MapControllerRoute(
    name: "default", 
    pattern: "{controller=Home}/{action=Index}/{id?}"); // маршрут по умолчанию (к контроллерам и их методам)

using (var scope = app.Services.CreateScope()) // вручную создаем один скоуп, чтобы до запуска приложения добавить роль преподавателя
{
    var roleManager = scope.ServiceProvider.GetRequiredService<RoleManager<IdentityRole>>();
    var userManager = scope.ServiceProvider.GetRequiredService<UserManager<IdentityUser>>();
    if (!await roleManager.RoleExistsAsync("Teacher"))
    {
        await roleManager.CreateAsync(new IdentityRole("Teacher"));
    }
    
    var teacher = await userManager.FindByEmailAsync("teacher@gmail.com");
    if (teacher != null && !await userManager.IsInRoleAsync(teacher, "Teacher"))
    {
        await userManager.AddToRoleAsync(teacher, "Teacher");
    }
}
app.Run();