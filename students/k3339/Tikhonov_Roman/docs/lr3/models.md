# ЛР3. Модели

Вариант 11 "Биржа труда". Серверная часть информационной системы на Django,
Django REST Framework и Djoser, СУБД PostgreSQL. ИС хранит сведения о
соискателях, вакансиях, работодателях, курсах переквалификации и пособиях;
поддерживает подбор вакансий, учёт заявок, назначение пособий и отчётов.

Девять сущностей по согласованной ER-схеме. Справочники и независимые
сущности: `Profession`, `Education`, `Employer`, `Course`, `Applicant`,
`Vacancy`; зависимые: `CourseEnrollment` (m2m "соискатель - курс" с
атрибутами), `Application` (m2m "соискатель - вакансия" с атрибутами),
`Allowance`.

Связи и политики удаления:

| Связь | Поле | on_delete | related_name |
|---|---|---|---|
| Profession - Applicant | `Applicant.profession` | PROTECT | `applicants` |
| Education - Applicant | `Applicant.education` | PROTECT | `applicants` |
| Profession - Vacancy | `Vacancy.profession` | PROTECT | `vacancies` |
| Education - Vacancy | `Vacancy.education` | PROTECT | `vacancies` |
| Employer - Vacancy | `Vacancy.employer` | PROTECT | `vacancies` |
| Profession - Course | `Course.profession` | PROTECT | `courses` |
| Applicant - CourseEnrollment | `CourseEnrollment.applicant` | CASCADE | `enrollments` |
| Course - CourseEnrollment | `CourseEnrollment.course` | CASCADE | `enrollments` |
| Applicant - Application | `Application.applicant` | CASCADE | `applications` |
| Vacancy - Application | `Application.vacancy` | CASCADE | `applications` |
| Applicant - Allowance | `Allowance.applicant` | CASCADE | `allowances` |
