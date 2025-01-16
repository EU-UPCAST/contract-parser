# contract-parser
A parser for ODRL contracts with convenience methods that encapsulate SPARQL queries that return commonly used information
Tested with Python 3.11


Usage:

Load a contract in .ttl or jsonld with the load method

You can get the IRIs of consumer and provider with get_consumer and get_provider

You can get a list of actions permitted in the contract using get_permitted_actions, from that list, you can query additional constraints per action (if specified in the contract):
  * get_action_container returns the url of the container that implements the action
  * get_action_execution_command returns the execution command that must be executed
  * get_action_execution_limits returns the number of execution limits (e.g. < 3 times , >= 1 time)
  * get_action_dependencies returns actions that must be executed before the input action 