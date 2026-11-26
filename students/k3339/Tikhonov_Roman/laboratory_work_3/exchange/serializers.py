from decimal import Decimal

from rest_framework import serializers

from .models import (
    Allowance,
    Applicant,
    Application,
    Course,
    CourseEnrollment,
    Education,
    Employer,
    Profession,
    Vacancy,
)


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = "__all__"


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = "__all__"

    def validate(self, attrs):
        salary_min = attrs.get("salary_min", getattr(self.instance, "salary_min", None))
        salary_max = attrs.get("salary_max", getattr(self.instance, "salary_max", None))
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError("Зарплата от не может превышать зарплату до")
        return attrs


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = "__all__"

    def validate(self, attrs):
        completion = attrs.get("completion_date", getattr(self.instance, "completion_date", None))
        rank = attrs.get("resulting_rank", getattr(self.instance, "resulting_rank", None))
        if completion and not rank:
            raise serializers.ValidationError(
                "При завершении курса требуется указать полученный разряд"
            )
        return attrs

    def create(self, validated_data):
        enrollment = super().create(validated_data)
        self.apply_completion(enrollment)
        return enrollment

    def update(self, instance, validated_data):
        enrollment = super().update(instance, validated_data)
        self.apply_completion(enrollment)
        return enrollment

    def apply_completion(self, enrollment):
        if enrollment.completion_date and enrollment.resulting_rank:
            applicant = enrollment.applicant
            applicant.rank = enrollment.resulting_rank
            applicant.save()


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"

    def validate(self, attrs):
        vacancy = attrs.get("vacancy", getattr(self.instance, "vacancy", None))
        status = attrs.get("status", getattr(self.instance, "status", Application.Status.PENDING))
        if (
            vacancy is not None
            and status == Application.Status.ACCEPTED
            and vacancy.status == Vacancy.Status.CLOSED
        ):
            raise serializers.ValidationError("Вакансия уже закрыта")
        return attrs

    def update(self, instance, validated_data):
        was_accepted = instance.status == Application.Status.ACCEPTED
        application = super().update(instance, validated_data)
        if application.status == Application.Status.ACCEPTED and not was_accepted:
            vacancy = application.vacancy
            vacancy.status = Vacancy.Status.CLOSED
            vacancy.save()
        return application


class AllowanceSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Allowance
        fields = "__all__"

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start is not None and end is not None and end < start:
            raise serializers.ValidationError("Дата окончания не может быть раньше даты начала")
        return attrs

    def create(self, validated_data):
        if "amount" not in validated_data:
            applicant = validated_data["applicant"]
            validated_data["amount"] = (applicant.last_salary * Decimal("0.6")).quantize(
                Decimal("0.01")
            )
        return super().create(validated_data)


class EnrollmentDetailSerializer(CourseEnrollmentSerializer):
    applicant = ApplicantSerializer(read_only=True)


class CourseApplicantsSerializer(CourseSerializer):
    enrollments = EnrollmentDetailSerializer(many=True, read_only=True)


class EmployerDetailSerializer(EmployerSerializer):
    vacancies = VacancySerializer(many=True, read_only=True)


class ApplicantDetailSerializer(ApplicantSerializer):
    applications = ApplicationSerializer(many=True, read_only=True)
    allowances = AllowanceSerializer(many=True, read_only=True)
    enrollments = CourseEnrollmentSerializer(many=True, read_only=True)
