"""
Insurance dApp
===================================

This dApp is an example of an insurance contract that pays out in case of
an external event, that is signalled by an oracle.

It has the following entities: the owner, customer, insurer (can be the owner
or a third party) and the oracle. The owner can initialize an agreement.
The oracle signals the result of the event, after which the customer,
insurer or owner can claim to pay out the insured amount/premium.
The oracle will also be paid for its services/costs.

In case the oracle fails to signal the result, the owner can refund both the
customer and insurer with the 'refundAll' operation.

"""
from boa.blockchain.vm.Neo.Runtime import Log, Notify, GetTrigger, CheckWitness
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader
from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete
from boa.code.builtins import list


# -------------------------------------------
# DAPP SETTINGS
# -------------------------------------------

OWNER = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
# Script hash of the token owner

THRESHOLD = 50
# Threshold of relative sunshine duration percent on a given day

# -------------------------------------------
# Events
# -------------------------------------------

DispatchAgreementEvent = RegisterAction('agreement', 'agreement_key')
DispatchResultNoticeEvent = RegisterAction('result-notice', 'agreement_key', 'weather_param', 'oracle_cost')
DispatchClaimEvent = RegisterAction('pay-out', 'agreement_key')
DispatchTransferEvent = RegisterAction('transfer', 'from', 'to', 'amount')
DispatchRefundAllEvent = RegisterAction('refund-all', 'agreement_key')
DispatchDeleteAgreementEvent = RegisterAction('delete', 'agreement_key')


def Main(operation, args):

    """
    This is the main entry point for the dApp
    :param operation: the operation to be performed
    :type operation: str
    :param args: an optional list of arguments
    :type args: list
    :return: indicating the successful execution of the dApp
    :rtype: bool
    """
    trigger = GetTrigger()

    if trigger == Verification():

        # if the script that sent this is the owner
        # we allow the spend
        is_owner = CheckWitness(OWNER)

        if is_owner:

            return True

        return False

    elif trigger == Application():

        if operation == 'deploy':
            if len(args) == 6:
                dapp_name = args[0]
                oracle = args[1]
                time_margin = args[2]
                min_time = args[3]
                max_time = args[4]
                fee = args[5]
                d = Deploy(dapp_name, oracle, time_margin, min_time, max_time)

                Log("Dapp deployed")
                return d
            else:
                return False

        elif operation == 'name':
            context = GetContext()
            n = Get(context, 'dapp_name')
            return n

        elif operation == 'updateName':
            if len(args) == 1:
                new_name = args[0]
                n = UpdateName(new_name)
                Log("Name updated")
                return n

            else:
                return False

        elif operation == 'oracle':
            context = GetContext()
            o = Get(context, 'oracle')

            return o

        elif operation == 'updateOracle':
            if len(args) == 1:
                new_oracle = args[0]
                o = UpdateOracle(new_oracle)
                Log("Oracle updated")
                return o

            else:
                return False

        elif operation == 'time_margin':
            context = GetContext()
            time_margin = Get(context, 'time_margin')

            return time_margin

        elif operation == 'min_time':
            context = GetContext()
            min_time = Get(context, 'min_time')

            return min_time

        elif operation == 'max_time':
            context = GetContext()
            max_time = Get(context, 'max_time')

            return max_time

        elif operation == 'updateTimeLimits':
            if len(args) == 2:
                time_variable = args[0]
                value = args[1]
                t = UpdateTimeLimits(time_variable, value)
                Log("Time limits updated")
                return t

            else:
                return False

        elif operation == 'agreement':
            if len(args) == 10:
                agreement_key = args[0]
                customer = args[1]
                insurer = args[2]
                location = args[3]
                timestamp = args[4]
                utc_offset = args[5]
                amount = args[6]
                premium = args[7]
                dapp_name = args[8]
                fee = args[9]
                a = Agreement(agreement_key, customer, insurer, location, timestamp, utc_offset, amount, premium, dapp_name, fee)

                Log("Agreement added!")
                return a

            else:
                return False

        elif operation == 'resultNotice':
            if len(args) == 3:
                agreement_key = args[0]
                weather_param = args[1]
                oracle_cost = args[2]
                return ResultNotice(agreement_key, weather_param, oracle_cost)

            else:
                return False

        elif operation == 'claim':
            if len(args) == 1:
                agreement_key = args[0]
                return Claim(agreement_key)

            else:
                return False

        elif operation == 'transfer':
            if len(args) == 3:
                t_from = args[0]
                t_to = args[1]
                t_amount = args[2]
                return DoTransfer(t_from, t_to, t_amount)

            else:
                return False

        elif operation == 'refundAll':
            if len(args) == 1:
                agreement_key = args[0]
                return RefundAll(agreement_key)

            else:
                return False

        elif operation == 'deleteAgreement':
            if len(args) == 1:
                agreement_key = args[0]
                return DeleteAgreement(agreement_key)

            else:
                return False

        result = 'unknown operation'

        return result

    return False


def Deploy(dapp_name, oracle, time_margin, min_time, max_time):
    """
    Method for the dApp owner initiate settings in storage

    :param dapp_name: name of the dapp
    :type dapp_name: str

    :param oracle: oracle that is used
    :type oracle: bytearray

    :param time_margin: time margin in seconds
    :type time_margin: int

    :param min_time: minimum time until the datetime of the event in seconds
    :type min_time: int

    :param max_time: max_time until the datetime of the event in seconds
    :type max_time: int

    :return: whether the update succeeded
    :rtype: bool
    """

    if not CheckWitness(OWNER):
        Log("Must be owner to deploy dApp")
        return False

    context = GetContext()
    Put(context, 'dapp_name', dapp_name)
    Put(context, 'oracle', oracle)

    if time_margin < 0:
        Log("time_margin must be positive")
        return False

    Put(context, 'time_margin', time_margin)

    if min_time < 3600 + time_margin:
        Log("min_time must be greater than 3600 + time_margin")
        return False

    Put(context, 'min_time', min_time)

    if max_time <= (min_time + time_margin):
        Log("max_time must be greather than min_time + time_margin")
        return False

    Put(context, 'max_time', max_time)

    return True


def UpdateName(new_name):
    """
    Method for the dApp owner to update the dapp name

    :param new_name: new name of the dapp
    :type new_name: str

    :return: whether the update succeeded
    :rtype: bool
    """

    if not CheckWitness(OWNER):
        Log("Must be owner to update name")
        return False

    context = GetContext()
    Put(context, 'dapp_name', new_name)

    return True


def UpdateOracle(new_oracle):
    """
    Method for the dApp owner to update oracle that is used to signal events

    :param new_name: new oracle for the dapp
    :type new_name: bytearray

    :return: whether the update succeeded
    :rtype: bool
    """

    if not CheckWitness(OWNER):
        Log("Must be owner to update oracle")
        return False

    context = GetContext()
    Put(context, 'oracle', new_oracle)

    return True


def UpdateTimeLimits(time_variable, value):
    """
    Method for the dApp owner to update the time limits

    :param time_variable: the name of the time variable to change
    :type time_variable: str

    :param value: the value for the time variable to change in seconds
    :type value: int

    :return: whether the update succeeded
    :rtype: bool
    """

    if not CheckWitness(OWNER):
        Log("Must be owner to update time limits")
        return False

    if value < 0:
        Log("Time limit value must be positive")
        return False

    context = GetContext()

    if time_variable == 'time_margin':
        time_margin = value
        Put(context, 'time_margin', time_margin)

    elif time_variable == 'min_time':
        min_time = value
        Put(context, 'min_time', min_time)

    elif time_variable == 'max_time':
        max_time = value
        Put(context, 'max_time', max_time)

    else:
        Log("Time variable name not existing")
        return False

    return True


def Agreement(agreement_key, customer, insurer, location, timestamp, utc_offset, amount, premium, dapp_name, fee):

    """
    Method to create an agreement

    :param agreement_key: unique identifier for the agreement
    :type agreement_key: str

    :param customer: customer party of the agreement
    :type customer: bytearray

    :param insurer: insurer party of the agreement
    :type insurer: bytearray

    :param location: location were the event occurs, typically a city
    :type location: str

    :param timestamp: timezone naive datetime of the day of the event
    :type timestamp: int

    :param utc_offset: positive or negative utc_offset for timestamp
    :type utc_offset: int

    :param amount: the insured amount of NEO
    :type amount: int

    :param premium: the amount of NEO to be paid as a premium to the insurer
    :type premium: int

    :param dapp_name: the name of the dApp
    :type dapp_name: str

    :param fee: the fee to be charged
    :type fee: int

    :return: whether the agreement was successful
    :rtype: bool
    """

    if not CheckWitness(OWNER):
        Log("Must be owner to add an agreement")
        return False

    # Check if the contract is deployed
    context = GetContext()
    if not Get(context, dapp_name):
        Log("Must first deploy contract with the deploy operation")
        return False

    # Get timestamp of current block
    currentHeight = GetHeight()
    currentBlock = GetHeader(currentHeight)
    current_time = currentBlock.Timestamp

    # Compute timezone adjusted time
    timezone_timestamp = timestamp + (utc_offset * 3600)
    timezone_current_time = current_time + (utc_offset * 3600)

    # Get contract settings
    dapp_name = Get(context, 'dapp_name')
    oracle = Get(context, 'oracle')
    time_margin = Get(context, 'time_margin')
    min_time = Get(context, 'min_time')
    max_time = Get(context, 'max_time')

    # Check if timestamp is not out of boundaries
    if timezone_timestamp < (timezone_current_time + min_time - time_margin):
        Log("Datetime must be > 1 day ahead")
        return False

    elif timezone_timestamp > (timezone_current_time + max_time + time_margin):
        Log("Datetime must be < 30 days ahead")
        return False

    # Check if amount and premium are not zero or below
    if amount <= 0:
        Log("Insured amount is zero or negative")
        return False

    if premium <= 0:
        Log("Premium is zero or negative")
        return False

    status = 'initialized'

    # Set place holder variables
    weather_param = 0
    oracle_cost = 0

    agreement_data = [customer, insurer, location, timestamp, utc_offset, amount, premium, fee, oracle, time_margin, min_time, max_time, status, weather_param, oracle_cost]

    Put(context, agreement_key, agreement_data)

    DispatchAgreementEvent(agreement_key)

    return True


def ResultNotice(agreement_key, weather_param, oracle_cost):
    """
    Method to signal resulte by oracle

    :param agreement_key: the key of the agreement
    :type agreement_key: bytearray

    :param weather_param: weather parameter that the contract is depending on
    :type weather_param: int

    :param oracle_cost: costs made by the oracle to do this assignment
    :type oracle_cost: int

    :return: whether a pay out to the customer is done
    :rtype: bool
    """

    # Check if the method is triggered by the oracle for this agreement
    context = GetContext()
    agreement_data = Get(context, agreement_key)
    oracle = agreement_data[8]

    if not CheckWitness(oracle):
        Log("Must be oracle to notice results")
        return False

    timestamp = agreement_data[3]
    utc_offset = agreement_data[4]
    status = agreement_data[12]

    if not status == 'initialized':
        Log("Contract has incorrect status to do a result notice")
        return False

    agreement_data[12] = 'result-noticed'
    agreement_data[13] = weather_param
    agreement_data[14] = oracle_cost

    # Get timestamp of current block
    currentHeight = GetHeight()
    currentBlock = GetHeader(currentHeight)
    current_time = currentBlock.Timestamp

    Put(context, agreement_key, agreement_data)

    timezone_timestamp = timestamp + (3600 * utc_offset)
    timezone_current_time = current_time + (3600 * utc_offset)

    if timezone_current_time < timezone_timestamp:
        Log("Datetime of result notice is lower than agreed datetime")
        return False
    else:
        DispatchResultNoticeEvent(agreement_key, weather_param, oracle_cost)
        return True


def Claim(agreement_key):
    """
    Method to handle the pay out

    :param agreement_key: the key of the agreement
    :type agreement_key: bytearray

    :return: whether a pay out to the customer is done
    :rtype: bool
    """

    context = GetContext()
    agreement_data = Get(context, agreement_key)
    customer = agreement_data[0]
    insurer = agreement_data[1]
    oracle = agreement_data[8]
    status = agreement_data[12]
    amount = agreement_data[5]
    premium = agreement_data[6]
    fee = agreement_data[7]
    weather_param = agreement_data[13]
    oracle_cost = agreement_data[14]

    # Check if the pay out is triggered by the owner, customer, or insurer.
    valid_witness = False

    if CheckWitness(OWNER):
        valid_witness = True

    elif CheckWitness(customer):
        valid_witness = True

    elif CheckWitness(insurer):
        valid_witness = True

    if not valid_witness:
        Log("Must be owner, customer or insurer to claim")
        return False

    # Check whether this contract has the right status to do a claim
    if status == 'initialized':
        Log("Status must be result-noticed to be able to do a claim")
        return False

    elif status == 'claimed':
        Log("Contract pay out is already claimed")
        return False

    elif status == 'refunded':
        Log("Contract is already refunded")
        return False

    net_premium = premium - fee

    if weather_param >= THRESHOLD:
        Notify("Day was sunny, no pay out to customer")
        DoTransfer(OWNER, insurer, net_premium)
        DispatchTransferEvent(OWNER, insurer, net_premium)
        return False

    elif weather_param < THRESHOLD:
        Notify("Day was not sunny, pay out insured amount to customer")
        DoTransfer(OWNER, insurer, net_premium)
        DispatchTransferEvent(OWNER, insurer, net_premium)
        DoTransfer(OWNER, customer, amount)
        DispatchTransferEvent(OWNER, customer, amount)

    DoTransfer(OWNER, oracle, oracle_cost)
    DispatchTransferEvent(OWNER, oracle, oracle_cost)

    agreement_data[12] = 'claimed'
    Put(context, agreement_key, agreement_data)
    DispatchClaimEvent(agreement_key)

    return True


def DoTransfer(sender, receiver, amount):
    """
    Method to transfer tokens from one account to another

    :param sender: the address to transfer from
    :type sender: bytearray

    :param receiver: the address to transfer to
    :type receiver: bytearray

    :param amount: the amount of tokens to transfer
    :type amount: int

    :return: whether the transfer was successful
    :rtype: bool

    """

    if amount <= 0:
        Log("Cannot transfer negative amount")
        return False

    from_is_sender = CheckWitness(sender)

    if not from_is_sender:
        Log("Not owner of funds to be transferred")
        return False

    if sender == receiver:
        Log("Sending funds to self")
        return True

    context = GetContext()
    from_val = Get(context, sender)

    if from_val < amount:
        Log("Insufficient funds to transfer")
        return False

    if from_val == amount:
        Delete(context, sender)

    else:
        difference = from_val - amount
        Put(context, sender, difference)

    to_value = Get(context, receiver)

    to_total = to_value + amount

    Put(context, receiver, to_total)
    DispatchTransferEvent(sender, receiver, amount)

    return True


def RefundAll(agreement_key):
    """
    Method refund payments in case a total eclipse or EMP caused oracle failure

    :param agreement_key: agreement_key
    :type agreement_key: bytearray

    :return: whether the refund was successful
    :rtype: bool

    """

    if not CheckWitness(OWNER):
        Log("Must be owner to do a refund to all")
        return False

    context = GetContext()
    agreement_data = Get(context, agreement_key)
    status = agreement_data[12]
    customer = agreement_data[0]
    insurer = agreement_data[1]
    status = agreement_data[12]
    amount = agreement_data[5]
    premium = agreement_data[6]
    fee = agreement_data[7]

    if status == 'claimed':
        Log("contract pay out has already been claimed")
        return False

    elif status == 'refunded':
        Log("A RefundAll already took place")
        return False

    # Perform refund
    net_premium = premium - fee
    DoTransfer(OWNER, insurer, net_premium)
    DispatchTransferEvent(OWNER, insurer, net_premium)
    DoTransfer(OWNER, customer, amount)
    DispatchTransferEvent(OWNER, customer, amount)

    agreement_data[12] = 'refunded'
    Put(context, agreement_key, agreement_data)
    DispatchRefundAllEvent(agreement_key)

    return True


def DeleteAgreement(agreement_key):
    """
    Method for the dApp owner to delete claimed or refunded agreements

    :param agreement_key: agreement_key
    :type agreement_key: str

    :return: whether the deletion succeeded
    :rtype: bool
    """

    if not CheckWitness(OWNER):
        Log("Must be owner to delete an agreement")
        return False

    context = GetContext
    agreement_data = Get(context, agreement_key)
    status = agreement_data[12]

    if status == 'claimed':
        Delete(context, agreement_key)
        DispatchDeleteAgreementEvent(agreement_key)

    elif status == 'refunded':
        Delete(context, agreement_key)
        DispatchDeleteAgreementEvent(agreement_key)

    return False
