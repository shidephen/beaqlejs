// configure the test here
var TestConfig = {
  "TestName": "{{testsuite_name}}",
  "LoopByDefault": true,
  "ShowFileIDs": false,
  "ShowResults": false,
  "EnableABLoop": true,
  "EnableOnlineSubmission": true,
  "BeaqleServiceURL": "submit",
  "SupervisorContact": "",
  "AudioRoot": "",
  "Testsets": [
    {% for test in tests %}
      {% block test %}
      {
        "Name": "{{ escape(test.name) }}",
        "TestID": "{{ escape(test.id) }}",
        "Files": {
          "A": "{{ escape(test.A) }}",
          "B": "{{ escape(test.B) }}"
        }
      },
      {% end %}
    {% end % }
  ]
}
