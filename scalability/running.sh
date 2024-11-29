wrk2 -t2 -c40 -d120s -R2000  -s \
scalability/wrk_multi_query.lua http://10.128.0.16:14240/restpp/query/g1/q1? \
> scalability/bigann/8-node/m1.log &

wrk2 -t2 -c40 -d120s -R2000  -s \
scalability/wrk_multi_query.lua http://10.128.0.5:14240/restpp/query/g1/q1? \
> scalability/bigann/8-node/m2.log &

wrk2 -t2 -c40 -d120s -R2000  -s \
scalability/wrk_multi_query.lua http://10.128.0.29:14240/restpp/query/g1/q1? \
> scalability/bigann/8-node/m3.log &

wrk2 -t2 -c40 -d120s -R2000  -s \
scalability/wrk_multi_query.lua http://10.128.0.33:14240/restpp/query/g1/q1? \
> scalability/bigann/8-node/m4.log &

wrk2 -t2 -c40 -d120s -R2000  -s \
scalability/wrk_multi_query.lua http://10.128.0.55:14240/restpp/query/g1/q1? \
> scalability/bigann/8-node/m5.log &

wrk2 -t2 -c40 -d120s -R2000  -s \
scalability/wrk_multi_query.lua http://10.128.0.59:14240/restpp/query/g1/q1? \
> scalability/bigann/8-node/m6.log &

wrk2 -t2 -c40 -d120s -R2000  -s \
scalability/wrk_multi_query.lua http://10.128.0.61:14240/restpp/query/g1/q1? \
> scalability/bigann/8-node/m7.log &

wrk2 -t2 -c40 -d120s -R2000  -s \
scalability/wrk_multi_query.lua http://10.128.0.62:14240/restpp/query/g1/q1? \
> scalability/bigann/8-node/m8.log &