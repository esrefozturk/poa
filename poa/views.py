from rest_framework import exceptions
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from models import Block, Transaction
from serializers import WaitingTransactionSerializer, BlockSerializer, NewBlockSerializer, TransactionSerializer
from utils import get_block_count


class BlockHandler(ListAPIView):
    serializer_class = BlockSerializer
    lookup_url_kwarg = 'hash'
    lookup_field = 'hash'

    def get_queryset(self):
        if self.kwargs.get('hash'):
            try:
                return Block.objects.filter(hash=self.kwargs['hash'])
            except:
                raise exceptions.NotFound()
        else:
            Block.objects.all()


class TransactionHandler(ListAPIView):
    serializer_class = TransactionSerializer
    lookup_url_kwarg = 'hash'
    lookup_field = 'hash'

    def get_queryset(self):
        if self.kwargs.get('hash'):
            try:
                return Transaction.objects.filter(hash=self.kwargs['hash'])
            except:
                raise exceptions.NotFound()
        else:
            Transaction.objects.all()


class WaitingTransactionHandler(CreateAPIView):
    serializer_class = WaitingTransactionSerializer


class ConsensusHandler(CreateAPIView):
    serializer_class = NewBlockSerializer


class BlockCountHandler(APIView):
    def get(self, request):
        return Response(get_block_count())
