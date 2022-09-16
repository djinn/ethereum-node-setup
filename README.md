# Ethereum One Click Node on AWS

The CDK automation lets you build a cost optimal Ethereum full node with AWS best practices. 

## Why use this automation?

The setup of Ethereum node is different from typical application setups. Ethereum put unique requirements on disk consumption. However, this also opens many opertunities to leverage AWS specific best practices. 

* Use of Graviton instead of Intel or AMD systems to save costs without compromising performance
* Using filesystem compression to pack the node data tightly saving some storage penny

## How to use the CDK automation?

```
$ cd cdk
$ source .venv/bin/activate
% pip install -r requirements.txt
% cdk synth
```
