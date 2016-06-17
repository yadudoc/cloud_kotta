# Cloud Kotta

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Recipes for a turnkey versatile cloud execution service. This is in production at https://turingcompute.net/
Some of the auxiliary systems are not included in the cloudformation document in the infrastructure folder
and must be setup manually.

*Use at your own risk*


## Setup

* Install boto, preferably inside virtualenv for testing.
```
pip install boto
```

* Update configs with user specific info.

* Run source setup.sh

* Run ./aws.py with no args to get a help message on supported operations.


Broker the best deals from Amazon

[Amazon Documentation](https://aws.amazon.com/blogs/aws/new-ec2-spot-instance-termination-notices/)

From the gospel of Amazon's documentation :
*_If your Spot Instance is interrupted by Amazon EC2, you will not be charged for the interrupted hour. For example, if your Spot Instance is interrupted 59 minutes after it starts, we will not charge you for that 59 minutes. However, if you terminate your instance, you will pay for any partial hour of usage as you would for On-Demand Instances._*

While several strategies are described in the internets for ensuring high availability at a lower cost, I have
yet to come across strategies for applications for which availability is desirable but not a requirement. This
might be because:

1. Stategies are trivial when availability is not a concern.
2. Very few applications/use-cases can work with low availability.

Since our primary concern is getting massive computational power at the cheapest price point with
less regard for high-availability and flexibility on time to completion, we can afford to :

1. Compute only when the price is within limits.
2. Engage in methods that involve higher risk of termination for cheaper compute.


The following bits need a lot more thinking:

Since we have timing considerations coming from hourly billing, a stateful service would most likely
be needed. If we were to maintain a pool of resources, we'd want to have control on when to terminate
resources, and we'd want to terminate them as close to the hourly billing mark as possible. Holding
a resource to the billing point, increases the odds of termination as well as extracts the most
compute time from the instance. At some point we might want some way of biasing new tasks/jobs to
fill available compute time slots on existing resources.

- Track the remaining compute time per instance, and fit incoming tasks to the instance with the
  best fit ? -Do we do best fit or greedy fit ? We atleast have the advantage of knowing a walltime
  for the apps.
    - This could be a bottomless rabbit hole. Almost like writing a scheduler from scratch.


The desired time to completion dictates the volume of instances/cores required and walltime per core.
  Deadline <= nCores*totalWallTime


Here are the rules:

*bidPrice determines the probability of eviction.*
 -Separate module to determine probability of eviction
    -Look at probability from history
    -smarter prediction can come later.

```
risk_cost_update(self, bidPrice, currentPrice, acceptable_risk)
    If projectedWaitTime > Deadline:
        self.acceptable_risk -= 1
        recompute_price(bidPrice, currentPrice)

engine(bidPrice,acceptable_risk)
    If bidPrice >= currentPrice :
        If instance.state == Running:
            risk_cost_update(self, bidPrice, currentPrice, acceptable_risk)
            check_workQueue(self)
        else:
            risk_


    else-if bidPrice <  currentPrice :
        If instance.state == Running:
             Wait for AWS to kill instance | We get free compute time
        If instance.state == Pending:
             risk_cost_update(self, bidPrice, currentPrice, acceptable_risk)

```

Notes from meeting with Mike:

The only reasonable predictions that could be made can be made from
looking at daily and weekly price patterns. 

