from django.urls import path

from . import views

urlpatterns = [
    path('agents/', views.AgentListCreateView.as_view()),
    path('agents/<int:pk>/', views.AgentDetailView.as_view()),

    path('employment-contracts/', views.EmploymentContractListCreateView.as_view()),
    path('employment-contracts/<int:pk>/', views.EmploymentContractDetailView.as_view()),

    path('organizations/', views.OrganizationListCreateView.as_view()),
    path('organizations/<int:pk>/', views.OrganizationDetailView.as_view()),
    path('organizations/<int:pk>/nested/', views.OrganizationNestedView.as_view()),

    path('individuals/', views.IndividualListCreateView.as_view()),
    path('individuals/<int:pk>/', views.IndividualDetailView.as_view()),

    path('risk-categories/', views.RiskCategoryListCreateView.as_view()),
    path('risk-categories/<int:pk>/', views.RiskCategoryDetailView.as_view()),

    path('contracts/', views.ContractListCreateView.as_view()),
    path('contracts/<int:pk>/', views.ContractDetailView.as_view()),
    path('contracts/<int:pk>/nested/', views.ContractNestedView.as_view()),

    path('tariffs/', views.ContractTariffListCreateView.as_view()),
    path('tariffs/<int:pk>/', views.ContractTariffDetailView.as_view()),

    path('insured-persons/', views.InsuredPersonListCreateView.as_view()),
    path('insured-persons/<int:pk>/', views.InsuredPersonDetailView.as_view()),

    path('insurance-cases/', views.InsuranceCaseListCreateView.as_view()),
    path('insurance-cases/<int:pk>/', views.InsuranceCaseDetailView.as_view()),

    path('analytics/organizations/<int:pk>/same-agents/', views.SameAgentsOrganizationsView.as_view()),
    path('analytics/agents/contracts-count/', views.AgentContractsCountView.as_view()),
    path('analytics/individuals/<int:pk>/colleagues/', views.PersonColleaguesView.as_view()),
    path('analytics/payouts-by-type/', views.PayoutsByTypeView.as_view()),
    path('analytics/organizations/report/', views.OrganizationReportView.as_view()),
    path('analytics/firm-report/', views.FirmReportView.as_view()),
]