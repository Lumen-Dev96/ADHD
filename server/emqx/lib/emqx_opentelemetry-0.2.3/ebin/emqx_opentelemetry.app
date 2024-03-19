{application,emqx_opentelemetry,
             [{description,"OpenTelemetry for EMQX Broker"},
              {vsn,"0.2.3"},
              {registered,[]},
              {mod,{emqx_otel_app,[]}},
              {applications,[kernel,stdlib,emqx,emqx_management,
                             opentelemetry_exporter,opentelemetry,
                             opentelemetry_experimental,opentelemetry_api,
                             opentelemetry_api_experimental]},
              {env,[]},
              {modules,[emqx_otel_api,emqx_otel_app,emqx_otel_config,
                        emqx_otel_metrics,emqx_otel_schema,emqx_otel_sup,
                        emqx_otel_trace]},
              {licenses,["Apache 2.0"]},
              {maintainers,["EMQX Team <contact@emqx.io>"]},
              {links,[{"Homepage","https://emqx.io/"},
                      {"Github","https://github.com/emqx/emqx"}]}]}.