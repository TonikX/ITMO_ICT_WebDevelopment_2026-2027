from rest_framework.permissions import BasePermission, SAFE_METHODS


def get_doctor(user):
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "doctor_profile", None)


def get_patient(user):
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "patient_profile", None)


class IsStaffOrDoctor(BasePermission):
    """
    IsStaffOrDoctor

    Staff or linked doctor account.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or get_doctor(request.user))
        )


class IsStaffDoctorOrPatient(BasePermission):
    """
    IsStaffDoctorOrPatient

    Any clinic role with a linked profile, or staff.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_staff
                or get_doctor(user)
                or get_patient(user)
            )
        )


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
