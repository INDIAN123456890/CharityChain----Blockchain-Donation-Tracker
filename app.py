import streamlit as st
import time
from blockchain.wallet import generate_wallet, sign_message
from blockchain.transaction import Transaction
from blockchain.node import create_network

st.set_page_config(page_title="CharityChain", layout="wide")

if "nodes" not in st.session_state:
    st.session_state.nodes = create_network(3, difficulty=3)
if "wallets" not in st.session_state:
    st.session_state.wallets = {"charity_1": generate_wallet()}
if "donors" not in st.session_state:
    st.session_state.donors = {}

st.title("💰 CharityChain — Blockchain Donation Tracker")

# Sidebar: create wallets
with st.sidebar:
    st.header("Accounts")
    if st.button("New Donor"):
        w = generate_wallet()
        key = f"donor_{len(st.session_state.donors)+1}"
        st.session_state.donors[key] = w
        st.success(f"Created {key}")
    if st.button("New Charity"):
        w = generate_wallet()
        key = f"charity_{len(st.session_state.wallets)+1}"
        st.session_state.wallets[key] = w
        st.success(f"Created {key}")

# Donation form
st.subheader("Make a Donation")
donor = st.selectbox("Donor", list(st.session_state.donors.keys()) or ["None"])
charity = st.selectbox("Charity", list(st.session_state.wallets.keys()))
amount = st.number_input("Amount", min_value=0.0, value=1.0)
node_sel = st.selectbox("Submit via Node", [n.node_id for n in st.session_state.nodes])

if st.button("Donate"):
    if donor == "None":
        st.error("No donor available.")
    else:
        donor_w = st.session_state.donors[donor]
        charity_w = st.session_state.wallets[charity]
        ts = time.time()
        msg = f"{donor_w['address']}{charity_w['address']}{amount}{ {'ts': ts} }{ts}"
        sig = sign_message(donor_w["private_key"], msg)

        tx = Transaction(
            donor_w["address"],
            charity_w["address"],
            amount,
            donor_w["public_key"],
            sig,
            {"ts": ts},
            timestamp=ts
        )
        node = next(n for n in st.session_state.nodes if n.node_id == node_sel)
        node.broadcast_transaction(tx)
        st.success("Donation submitted!")

# Mining
st.subheader("Mining")
miner_node = st.selectbox("Miner Node", [n.node_id for n in st.session_state.nodes])
miner_wallets = {**st.session_state.donors, **st.session_state.wallets}
miner = st.selectbox("Miner Account", list(miner_wallets.keys()))
if st.button("Mine Block"):
    node = next(n for n in st.session_state.nodes if n.node_id == miner_node)
    addr = miner_wallets[miner]["address"]
    blk = node.mine_and_broadcast(addr)
    if blk:
        st.success(f"Mined Block {blk.index}")
    else:
        st.info("No transactions to mine.")

# Explorer
st.subheader("Blockchain Explorer")
node_exp = st.selectbox("View Node", [n.node_id for n in st.session_state.nodes])
node = next(n for n in st.session_state.nodes if n.node_id == node_exp)
st.write(f"Chain Length: {len(node.blockchain.chain)}")

for blk in node.blockchain.chain:
    with st.expander(f"Block {blk.index}"):
        st.json(blk.to_dict())

# Smart Contract Layer
st.subheader("Smart Contract State")
st.write("Donations:", node.contract.donations)
st.write("Charity Balances:", node.contract.charity_balances)
st.write("Donor Balances (crypto left):", node.contract.donor_balances)


# Withdrawal Section
st.subheader("Withdraw Funds")
charity_sel = st.selectbox("Select Charity for Withdrawal", list(st.session_state.wallets.keys()))
if st.button("Withdraw"):
    try:
        charity_addr = st.session_state.wallets[charity_sel]["address"]
        event = node.contract.withdraw(charity_addr)
        st.success(f"Withdrawal successful: {event}")
    except Exception as e:
        st.error(str(e))

# Contract Events
st.subheader("Contract Events")
for event in node.contract.events:
    st.json(event)


