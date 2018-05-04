import hashlib

from sawtooth_sdk.processor.exceptions import InternalError
FAMILY_NAME="hellotxp"

#Addresses must be a 70 character hexadecimal string
#The first 6 characters of the address are the first 6 characters of a sha512 hash of the transactionprocessor namespace prefix: eg. testproc
HELLOTXP_ADDRESS_PREFIX = hashlib.sha512(FAMILY_NAME.encode('utf-8')).hexdigest()[0:6]

#The following 64 characters of the address are the last 64 characters of a sha512 hash of the entry Name
def _make_hellotxp_address(name):
    return HELLOTXP_ADDRESS_PREFIX + hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]

class HarvestBatch(object):
    def __init__(self,coopname,batchnr, latitude=None,longitude=None):
        self.coopname = coopname,
        self.batchnr = batchnr
       # self.latlong = "lat: " + latitude + " long: " + longitude

class HelloState(object):

    TIMEOUT = 3

    def __init__(self, context):
        """
        Args:
        context (sawtooth_sdk.transactionprocessor.context.Context): Access to
            validator state from within the transaction transactionprocessor.
        """
        self._context = context
        self._address_cache = {}

        print(context)

    def delete_batch(self,name):
        """
        deletes the batch numbered by batchnr from state
        :param batchnr: batch number
         """
        batches = self._load_batches(name=name)

        del batches[name]
        if batches:
            self._store_batch(name, batches = batches)
        else:
            self._delete_batch(name)

    def set_batch(self, name, harvestbatch):
        """
        Stores the Co-op's harvest batch in validator state

        :param batchnr: number of the batch
        :param coop: information of coop

        """
        print(harvestbatch)
        batches = self._load_batches(name=name)

        batches[name] = harvestbatch

        self._store_batch(name, batches=batches)
        print("set batch in validator state")

    def get_batch(self, name):
        """
        Get the batch associated with batchnr
        :param batchnr: the associated batchnr
        :return: all the information specifying a harvestbatch
        """

        return self._load_batches(name).get(name)

    def _store_batch(self, name, batches):
        """
        store harvest batch on the tree

        By convention, we’ll store batch data at an address obtained from hashing the harvest batch name prepended with some constant.

       'hellotxp' data is stored in state using addresses generated from the 'hellotxp' family name and the batchnr being stored.
        In particular, an 'hellotxp' address consists of the first 6 characters of the SHA-512 hash of the UTF-8 encoding of the string “hellotxp” (which is “314d67”)
        plus the first 64 characters of the SHA-512 hash of the UTF-8 encoding of the batchnr. for example 314d677ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff

        :param batchnr: batchnr of the associated batch
        :param batches:list of batches
        :return:
        """
        nameToSet = name
        address = _make_hellotxp_address(nameToSet)

        state_data = self._serialize(batches)
        self._address_cache[address] = state_data
        self._context.set_state({address: state_data},timeout=self.TIMEOUT)
        print("stored batch")

    def _delete_batch(self,name):

        address = _make_hellotxp_address(name)

        self._context.delete_state(
            [address],
            timeout=self.TIMEOUT)

        self._address_cache[address] = None

    def _load_batches(self, name):
        print("name in load batches is: " + name)
        print("address created")
        address = _make_hellotxp_address(name)
        print(address)

        if address in self._address_cache:
            print("serializing batches")
            if self._address_cache[address]:
                serialized_batches = self._address_cache[address]
                batches = self._deserialize(serialized_batches)
            else:
                batches = {}
        else:
            print("start else loading batches")
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT
            )
            print(state_entries)
            if state_entries:
                self._address_cache[address] = state_entries[0].data
                batches = self._deserialize(data=state_entries[0].data)
            else:
                self._address_cache[address] = None
                batches = {}
        print(batches)
        return batches

    def _deserialize(self,data):
        """
        take bytes stored in state and deserialize them into python objects
        :param data: the utf-8 encoded string stored in state
        :return: (dict):batchnr and harvest batch values
        """
        batches = {}
        try:
            for batch in data.decode().split("|"):
                coopname,batchnr = batch.split(",")
                batches[batchnr] = HarvestBatch(coopname,batchnr)
        except ValueError:
            raise  InternalError("Failed to deserialize batch data")

        return batches

    def _serialize(self,batches):
        """
        takes a dict of harvestbatch objects and serializes them into bytes.


        :param batches:
        :return: the utf-8 encoded string stored in state.
        """

        batch_strs = []
        for name, b in batches.items():
            batch_str = ",".join(
                [name,b.batchnr]
            )
            print(name)
            batch_strs.append(batch_str)
        print(batch_strs)
        return "|".join(sorted(batch_strs)).encode()












