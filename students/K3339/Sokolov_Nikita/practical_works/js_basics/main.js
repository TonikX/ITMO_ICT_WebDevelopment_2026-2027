const courseName = "Веб-программирование"
let year = 2026
const isPractice = true

document.getElementById("types-out").textContent = [
  `courseName: ${typeof courseName} = ${courseName}`,
  `year: ${typeof year} = ${year}`,
  `isPractice: ${typeof isPractice} = ${isPractice}`,
].join("\n")

const people = [
  { name: "Анна", role: "студент" },
  { name: "Игорь", role: "ментор" },
  { name: "Мария", role: "студент" },
]

const list = document.getElementById("people-list")
people
  .filter((p) => p.role === "студент")
  .map((p) => p.name.toUpperCase())
  .forEach((name) => {
    const li = document.createElement("li")
    li.textContent = name
    list.appendChild(li)
  })

function add(a, b) {
  return a + b
}

const square = (n) => n * n

document.getElementById("sum-out").textContent = String(add(3, 5))
document.getElementById("square-out").textContent = String(square(7))

const greetBtn = document.getElementById("greet-btn")
const nameInput = document.getElementById("name-input")
const greetOut = document.getElementById("greet-out")

greetBtn.addEventListener("click", () => {
  const name = nameInput.value.trim() || "гость"
  greetOut.textContent = `Привет, ${name}!`
})

function loadDemoData() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        ok: true,
        items: ["Vue", "DRF", "CORS"],
        loadedAt: new Date().toISOString(),
      })
    }, 400)
  })
}

document.getElementById("load-btn").addEventListener("click", async () => {
  const out = document.getElementById("async-out")
  out.textContent = "Загрузка..."
  try {
    const data = await loadDemoData()
    out.textContent = JSON.stringify(data, null, 2)
  } catch (e) {
    out.textContent = "Ошибка загрузки"
  }
})
