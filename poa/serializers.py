from rest_framework import serializers

from models import WaitingTransaction, Block, Transaction, NewBlock


class WaitingTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingTransaction
        fields = ('sender', 'receiver', 'amount')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('sender', 'receiver', 'amount', 'hash')


class BlockSerializer(serializers.ModelSerializer):
    transactions = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ('index', 'timestamp', 'sign', 'hash', 'previous_hash', 'transactions', 'payload', 'miner')

    def get_transactions(self, block):
        return [
            TransactionSerializer(i).data for i in block.transactions.all()
        ]


class NewBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewBlock
        fields = ('index', 'timestamp', 'sign', 'hash', 'previous_hash', 'payload', 'miner')
