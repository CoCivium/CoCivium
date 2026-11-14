// Framework-only deterministic negative tests; no native tray is launched.
using CoCivium.CoGuardian;
using System.Text.Json;

internal static class ContractTests
{
    private static readonly DateTimeOffset Now =
        new(2026, 11, 14, 17, 40, 0, TimeSpan.Zero);
    private static int count;

    private static string Valid(
        string workId = "synthetic:mule-check",
        string dataClass = "PUBLIC_SYNTHETIC",
        string observed = "2026-11-14T17:39:30Z",
        int ttl = 120,
        bool receiverAck = false,
        string effectClass = "OBSERVE_ONLY",
        string schema = MuleObservation.Schema)
        => JsonSerializer.Serialize(new Dictionary<string, object>
        {
            ["schema"] = schema,
            ["work_id"] = workId,
            ["data_class"] = dataClass,
            ["observed_at_utc"] = observed,
            ["ttl_seconds"] = ttl,
            ["receiver_ack"] = receiverAck,
            ["effect_class"] = effectClass
        });

    private static void Check(string name, bool condition)
    {
        if (!condition)
            throw new Exception("FAIL_" + name);
        count++;
        Console.WriteLine("PASS " + name);
    }

    public static int Main()
    {
        var ok = MuleObservation.Read(Valid(), Now);
        Check("typed_fresh_sample_is_only_unverified_source",
              ok.Code == "SOURCE_FRESH__RECEIVER_UNVERIFIED" &&
              ok.SourceFresh && !ok.ReceiverAuthenticated &&
              !ok.RealWorkCompleted && ok.WorkId == "synthetic:mule-check");

        var absent = MuleObservation.Read(null, Now);
        Check("missing_source_holds", absent.Code == "HOLD_SOURCE_UNBOUND_OR_OVERSIZE");
        Check("malformed_json_holds", MuleObservation.Read("{", Now).Code == "HOLD_JSON");
        Check("changed_schema_holds", MuleObservation.Read(
              Valid(schema: "CoGuardian.Live.Mule"), Now).Code == "HOLD_SCHEMA");
        Check("private_source_holds", MuleObservation.Read(
              Valid(dataClass: "PRIVATE"), Now).Code == "HOLD_PRIVACY");
        Check("source_expired_holds", MuleObservation.Read(
              Valid(observed: "2026-11-14T17:30:00Z"), Now).Code == "HOLD_STALE_SOURCE");
        Check("future_event_holds", MuleObservation.Read(
              Valid(observed: "2026-11-14T17:45:00Z"), Now).Code == "HOLD_FUTURE_SOURCE");
        Check("forged_receiver_ack_holds", MuleObservation.Read(
              Valid(receiverAck: true), Now).Code == "HOLD_UNQUALIFIED_RECEIVER_ACK");
        Check("effect_escalation_holds", MuleObservation.Read(
              Valid(effectClass: "EXECUTE"), Now).Code == "HOLD_EFFECT_CLASS");
        Check("invalid_workid_holds", MuleObservation.Read(
              Valid(workId: "../private"), Now).Code == "HOLD_WORKID");
        Check("overlong_workid_holds", MuleObservation.Read(
              Valid(workId: new string('a', 129)), Now).Code == "HOLD_WORKID");
        Check("ttl_out_of_range_holds", MuleObservation.Read(
              Valid(ttl: 99999), Now).Code == "HOLD_TTL");
        Check("invalid_clock_holds", MuleObservation.Read(
              Valid(), Now.ToOffset(TimeSpan.FromHours(-5))).Code == "HOLD_CLOCK_NOT_UTC");

        var parsed = JsonDocument.Parse(Valid());
        var pairs = parsed.RootElement.EnumerateObject()
            .Select(p => "\"" + p.Name + "\":" + p.Value.GetRawText()).ToArray();
        var dup = "{" + string.Join(",", pairs) + ",\"work_id\":\"forged\"}";
        Check("duplicate_key_holds", MuleObservation.Read(
              dup, Now).Code == "HOLD_UNKNOWN_OR_DUPLICATE_FIELD");
        var injected = Valid().Replace("\"effect_class\"", "\"untrusted_command\":123,\"effect_class\"");
        Check("extra_command_field_holds", MuleObservation.Read(
              injected, Now).Code == "HOLD_UNKNOWN_OR_DUPLICATE_FIELD");
        Check("unbounded_json_holds", MuleObservation.Read(
              new string(' ', 9000), Now).Code == "HOLD_SOURCE_UNBOUND_OR_OVERSIZE");

        Check("invisible_effects_always_false",
              !MuleObservation.Read(Valid(), Now).ReceiverAuthenticated &&
              !MuleObservation.Read(Valid(), Now).RealWorkCompleted);
        Console.WriteLine("COGUARDIAN_MULE_SHADOW_CONTRACT_PASS=" + count);
        return 0;
    }
}
