from datetime import date

from django.db.models import Count, Q, Sum
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Agent,
    Contract,
    ContractTariff,
    EmploymentContract,
    Individual,
    InsuredPerson,
    InsuranceCase,
    Organization,
    RiskCategory,
)
from .serializers import (
    AgentSerializer,
    ContractDetailSerializer,
    ContractSerializer,
    ContractTariffSerializer,
    EmploymentContractSerializer,
    IndividualSerializer,
    InsuredPersonSerializer,
    InsuranceCaseSerializer,
    OrganizationDetailSerializer,
    OrganizationSerializer,
    RiskCategorySerializer, InsuredPersonNestedSerializer, TariffNestedSerializer,
)


class AgentListCreateView(generics.ListCreateAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer


class AgentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer



class EmploymentContractListCreateView(generics.ListCreateAPIView):
    queryset = EmploymentContract.objects.all()
    serializer_class = EmploymentContractSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EmploymentContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmploymentContract.objects.all()
    serializer_class = EmploymentContractSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]



class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationNestedView(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationDetailSerializer



class IndividualListCreateView(generics.ListCreateAPIView):
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer


class IndividualDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer



class RiskCategoryListCreateView(generics.ListCreateAPIView):
    queryset = RiskCategory.objects.all()
    serializer_class = RiskCategorySerializer


class RiskCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RiskCategory.objects.all()
    serializer_class = RiskCategorySerializer



class ContractListCreateView(generics.ListCreateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer


class ContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer


class ContractNestedView(generics.RetrieveAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractDetailSerializer



class ContractTariffListCreateView(generics.ListCreateAPIView):
    queryset = ContractTariff.objects.all()
    serializer_class = ContractTariffSerializer


class ContractTariffDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContractTariff.objects.all()
    serializer_class = ContractTariffSerializer



class InsuredPersonListCreateView(generics.ListCreateAPIView):
    queryset = InsuredPerson.objects.all()
    serializer_class = InsuredPersonSerializer


class InsuredPersonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InsuredPerson.objects.all()
    serializer_class = InsuredPersonSerializer



class InsuranceCaseListCreateView(generics.ListCreateAPIView):
    queryset = InsuranceCase.objects.all()
    serializer_class = InsuranceCaseSerializer


class InsuranceCaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InsuranceCase.objects.all()
    serializer_class = InsuranceCaseSerializer



def get_period(request):
    try:
        date_from = date.fromisoformat(request.query_params['date_from'])
        date_to = date.fromisoformat(request.query_params['date_to'])
    except (KeyError, ValueError):
        return None, None
    return date_from, date_to


class SameAgentsOrganizationsView(APIView):
    """ для заданной организации - другие организации, застрахованные
    теми же агентами, по действующим договорам
    """

    def get(self, request, pk):
        today = date.today()
        agents = Agent.objects.filter(
            contracts__organization_id=pk,
            contracts__start_date__lte=today,
            contracts__end_date__gte=today,
        ).distinct()
        organizations = Organization.objects.filter(
            contracts__agent__in=agents,
            contracts__start_date__lte=today,
            contracts__end_date__gte=today,
        ).exclude(id=pk).distinct()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)


class AgentContractsCountView(APIView):
    """ количество договоров каждого типа у каждого агента за период """

    def get(self, request):
        date_from, date_to = get_period(request)
        if date_from is None:
            return Response(
                {'error': 'Укажите параметры date_from и date_to (формат YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        agents = Agent.objects.annotate(
            collective_count=Count('contracts', filter=Q(
                contracts__contract_type=Contract.COLLECTIVE,
                contracts__conclusion_date__gte=date_from,
                contracts__conclusion_date__lte=date_to,
            )),
            individual_count=Count('contracts', filter=Q(
                contracts__contract_type=Contract.INDIVIDUAL,
                contracts__conclusion_date__gte=date_from,
                contracts__conclusion_date__lte=date_to,
            )),
        )
        data = [
            {
                'agent': str(agent),
                'collective_count': agent.collective_count,
                'individual_count': agent.individual_count,
            }
            for agent in agents
        ]
        return Response(data)


class PersonColleaguesView(APIView):
    """ зля заданной персоны - застрахованные сотрудники того же
    действующего коллективного договора """

    def get(self, request, pk):
        today = date.today()
        contracts = Contract.objects.filter(
            contract_type=Contract.COLLECTIVE,
            start_date__lte=today,
            end_date__gte=today,
            insured_persons__individual_id=pk,
        ).distinct()
        data = []
        for contract in contracts:
            insured = contract.insured_persons.all()
            data.append({
                'contract_id': contract.id,
                'organization': str(contract.organization),
                'end_date': contract.end_date,
                'insured_persons': InsuredPersonNestedSerializer(insured, many=True).data,
            })
        return Response(data)


class PayoutsByTypeView(APIView):
    """ общая сумма выплат по каждому типу договоров при страховых
    случаях за период """

    def get(self, request):
        date_from, date_to = get_period(request)
        if date_from is None:
            return Response(
                {'error': 'Укажите параметры date_from и date_to (формат YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cases = InsuranceCase.objects.filter(
            case_date__gte=date_from,
            case_date__lte=date_to,
        )
        data = []
        for contract_type, display in Contract.CONTRACT_TYPE_CHOICES:
            total = cases.filter(
                insured_person__contract__contract_type=contract_type,
            ).aggregate(total=Sum('payout_amount'))['total']
            data.append({
                'contract_type': display,
                'total_payout': total or 0,
            })
        return Response(data)


class OrganizationReportView(APIView):
    """ для каждого юрлица - реквизиты договоров и суммы
    выплат по категориям риска """

    def get(self, request):
        data = []
        for organization in Organization.objects.all():
            contracts_data = []
            for contract in organization.contracts.all():
                total = contract.tariffs.aggregate(
                    total=Sum('payout_amount'),
                )['total']
                contracts_data.append({
                    'contract_id': contract.id,
                    'contract_type': contract.get_contract_type_display(),
                    'conclusion_date': contract.conclusion_date,
                    'start_date': contract.start_date,
                    'end_date': contract.end_date,
                    'agent': str(contract.agent),
                    'tariffs': TariffNestedSerializer(
                        contract.tariffs.all(), many=True).data,
                    'total_payout': total,
                })
            data.append({
                'organization': str(organization),
                'contracts': contracts_data,
            })
        return Response(data)


class FirmReportView(APIView):
    """ отчет по фирме: действующие договоры каждого типа у работающих
    агентов, страховые суммы по типу и агенту, итог по фирме """

    def get(self, request):
        today = date.today()
        active_contracts = Contract.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
        )
        working_agents = Agent.objects.filter(
            employment_contracts__fire_date__isnull=True,
        ).distinct()

        agents_data = []
        for agent in working_agents:
            agent_contracts = active_contracts.filter(agent=agent)
            collective_sum = ContractTariff.objects.filter(
                contract__in=agent_contracts.filter(contract_type=Contract.COLLECTIVE),
            ).aggregate(total=Sum('payout_amount'))['total'] or 0
            individual_sum = ContractTariff.objects.filter(
                contract__in=agent_contracts.filter(contract_type=Contract.INDIVIDUAL),
            ).aggregate(total=Sum('payout_amount'))['total'] or 0
            agents_data.append({
                'agent': str(agent),
                'active_collective_count': agent_contracts.filter(
                    contract_type=Contract.COLLECTIVE).count(),
                'active_individual_count': agent_contracts.filter(
                    contract_type=Contract.INDIVIDUAL).count(),
                'collective_insured_sum': collective_sum,
                'individual_insured_sum': individual_sum,
            })

        firm_total_sum = ContractTariff.objects.filter(
            contract__in=active_contracts,
        ).aggregate(total=Sum('payout_amount'))['total'] or 0

        data = {
            'agents': agents_data,
            'firm': {
                'active_collective_count': active_contracts.filter(
                    contract_type=Contract.COLLECTIVE).count(),
                'active_individual_count': active_contracts.filter(
                    contract_type=Contract.INDIVIDUAL).count(),
                'total_insured_sum': firm_total_sum,
            },
        }
        return Response(data)