import hashlib

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
import random
# have a random number for batchnr (test purpose)
import sys
sys.path.append('../')
from helloPayload import HelloPayload
from helloState import HelloState, HarvestBatch
from helloState import FAMILY_NAME
from helloState import HELLOTXP_ADDRESS_PREFIX

# HelloTransactionHandler extends the transactionhandler


class HelloTransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['0.1']

    @property
    def namespaces(self):
        return [HELLOTXP_ADDRESS_PREFIX]

    # Handlers get called in two ways, with an "apply" method and with "metadata" methods.
    #  metadata methods provide connection between handler and transactionprocessor.
    # The bulk of the handler is made up of "apply" and its helper functions
    # the transaction parameter holds the command that is to be executed,
    #  it contains payloadbytes that are transaction family specific
    # context parameter stores information about the current state

    def apply(self, transaction, context):
        print("create transaction header")
        header = transaction.header
        signer = header.signer_public_key
        print("payload")
        hello_payload = HelloPayload.from_bytes(transaction.payload)
        print(hello_payload)
        print("state is put away")

        hello_state = HelloState(context)
        print(hello_state)
        print("start create batch")
        print(hello_payload.batchnr)
        print(hello_payload)
        if hello_payload.action == 'create':

            #new_batchnr = random.randint(1,50)
            #print(new_batchnr)
            print(hello_payload.name)
            if hello_state.get_batch(hello_payload.name) is not None:
                print("file exists")
                raise InvalidTransaction(
                    'Invalid action: Batch already exists: {}'.format(hello_payload.name)
                )
            print("creating a new  batch")
            batch = HarvestBatch(coopname=hello_payload.name,
                                 batchnr=hello_payload.batchnr,
                                # latitude=hello_payload.latitude,
                                # longitude=hello_payload.longitude
                                )

            print("batch created ")
            hello_state.set_batch(hello_payload.name,batch)
            print("get state")
        if hello_payload.action == 'delete':
            harvestbatch=hello_state.get_batch(hello_payload.name)
            if harvestbatch is None:
                raise InvalidTransaction('Invalid action: batch does not exist')
            hello_state.delete_batch(hello_payload.name)

        if hello_payload.action == 'update':
            batch = hello_state.get_batch(hello_payload.name)

            if batch is None:
                raise InvalidTransaction(
                    'Invalid action: No batch found to update by this name'
                )

        # update_batch = hello_state.



