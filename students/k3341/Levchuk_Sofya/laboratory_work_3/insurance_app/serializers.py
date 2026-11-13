from rest_framework import serializers
from .models import *


class AgentSerializer(serializers.ModelSerializer):
    """ страховой агент """

    class Meta:
        model = Agent
        fields = '__all__'


class EmploymentContractSerializer(serializers.ModelSerializer):
    """ трудовой договор агента (приём на работу и увольнение) """

    class Meta:
        model = EmploymentContract
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    """ организация """

    class Meta:
        model = Organization
        fields = '__all__'


class IndividualSerializer(serializers.ModelSerializer):
    """ физлицо """

    class Meta:
        model = Individual
        fields = '__all__'


class RiskCategorySerializer(serializers.ModelSerializer):
    """ категория риска """

    class Meta:
        model = RiskCategory
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    """ страховой договор """

    contract_type_display = serializers.CharField(
        source='get_contract_type_display', read_only=True,
    )

    class Meta:
        model = Contract
        fields = [
            'id', 'contract_type', 'contract_type_display',
            'conclusion_date', 'start_date', 'end_date',
            'agent', 'organization', 'individual',
        ]


class ContractTariffSerializer(serializers.ModelSerializer):
    """ тариф договора: сумма выплат по категории риска """

    class Meta:
        model = ContractTariff
        fields = '__all__'


class InsuredPersonSerializer(serializers.ModelSerializer):
    """ застрахованный сотрудник в договоре """

    class Meta:
        model = InsuredPerson
        fields = '__all__'


class InsuranceCaseSerializer(serializers.ModelSerializer):
    """ страховой случай """

    decision_display = serializers.CharField(
        source='get_decision_display', read_only=True,
    )

    class Meta:
        model = InsuranceCase
        fields = [
            'id', 'insured_person', 'case_date', 'reason',
            'decision', 'decision_display', 'payout_amount',
        ]



class TariffNestedSerializer(serializers.ModelSerializer):
    """ тариф, вложенный в договор: категория риска строкой и сумма """

    risk_category = serializers.StringRelatedField()

    class Meta:
        model = ContractTariff
        fields = ['risk_category', 'payout_amount']


class InsuredPersonNestedSerializer(serializers.ModelSerializer):
    """ застрахованный, вложенный в договор: ФИО, возраст, категория риска """

    individual = serializers.StringRelatedField()
    age = serializers.IntegerField(source='individual.age', read_only=True)
    risk_category = serializers.StringRelatedField()

    class Meta:
        model = InsuredPerson
        fields = ['id', 'individual', 'age', 'risk_category']


class ContractDetailSerializer(serializers.ModelSerializer):
    """ договор с вложенными объектами. tariffs (договор -> категории риска) и insured_persons (договор -> застрахованные физлица) """

    agent = serializers.StringRelatedField()
    organization = serializers.StringRelatedField()
    individual = serializers.StringRelatedField()
    contract_type_display = serializers.CharField(
        source='get_contract_type_display', read_only=True,
    )
    tariffs = TariffNestedSerializer(many=True, read_only=True)
    insured_persons = InsuredPersonNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'contract_type', 'contract_type_display',
            'conclusion_date', 'start_date', 'end_date',
            'agent', 'organization', 'individual',
            'tariffs', 'insured_persons',
        ]


class OrganizationDetailSerializer(serializers.ModelSerializer):
    """ организация с вложенными договорами - связь "один-ко-многим" """

    contracts = ContractSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'code', 'full_name', 'short_name',
            'address', 'bank_number', 'specialization', 'contracts',
        ]
