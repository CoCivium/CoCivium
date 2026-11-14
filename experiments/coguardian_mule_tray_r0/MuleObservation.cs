// Read-only model shared by the native shadow tray and its cross-platform tests.
// A syntactically valid source observation is not an authenticated receiver ACK.
using System.Globalization;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace CoCivium.CoGuardian;

public sealed record MuleState(string Code, string WorkId, bool SourceFresh)
{
    public bool ReceiverAuthenticated => false;
    public bool RealWorkCompleted => false;
}

public static class MuleObservation
{
    public const string Schema = "CoGuardian.Mule.Observation.R0";
    private static readonly Regex WorkIdShape =
        new(@"^[a-zA-Z0-9._:-]{1,128}$", RegexOptions.CultureInvariant);
    private static readonly Regex UtcShape =
        new(@"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$", RegexOptions.CultureInvariant);
    private static readonly HashSet<string> Fields = new(StringComparer.Ordinal)
    {
        "schema", "work_id", "data_class", "observed_at_utc",
        "ttl_seconds", "receiver_ack", "effect_class"
    };
    private static MuleState Hold(string code) => new(code, "NONE", false);

    public static MuleState Read(string? data, DateTimeOffset now)
    {
        if (string.IsNullOrWhiteSpace(data) || data.Length > 8192)
            return Hold("HOLD_SOURCE_UNBOUND_OR_OVERSIZE");
        if (now.Offset != TimeSpan.Zero)
            return Hold("HOLD_CLOCK_NOT_UTC");
        try
        {
            using var document = JsonDocument.Parse(data, new JsonDocumentOptions
            {
                CommentHandling = JsonCommentHandling.Disallow,
                AllowTrailingCommas = false,
                MaxDepth = 8
            });
            var root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object)
                return Hold("HOLD_SCHEMA");
            var observedFields = new HashSet<string>(StringComparer.Ordinal);
            int count = 0;
            foreach (var property in root.EnumerateObject())
            {
                count++;
                if (!Fields.Contains(property.Name) || !observedFields.Add(property.Name))
                    return Hold("HOLD_UNKNOWN_OR_DUPLICATE_FIELD");
            }
            if (count != Fields.Count)
                return Hold("HOLD_SCHEMA");
            if (root.GetProperty("schema").ValueKind != JsonValueKind.String ||
                root.GetProperty("schema").GetString() != Schema)
                return Hold("HOLD_SCHEMA");
            if (root.GetProperty("data_class").ValueKind != JsonValueKind.String ||
                root.GetProperty("data_class").GetString() != "PUBLIC_SYNTHETIC")
                return Hold("HOLD_PRIVACY");
            if (root.GetProperty("effect_class").ValueKind != JsonValueKind.String ||
                root.GetProperty("effect_class").GetString() != "OBSERVE_ONLY")
                return Hold("HOLD_EFFECT_CLASS");
            // The native shadow has no authenticated receiver principal.
            // An attempted positive ACK must be refused, never displayed green.
            if (root.GetProperty("receiver_ack").ValueKind != JsonValueKind.False)
                return Hold("HOLD_UNQUALIFIED_RECEIVER_ACK");
            if (root.GetProperty("work_id").ValueKind != JsonValueKind.String)
                return Hold("HOLD_WORKID");
            string? workId = root.GetProperty("work_id").GetString();
            if (workId is null || !WorkIdShape.IsMatch(workId))
                return Hold("HOLD_WORKID");
            if (root.GetProperty("ttl_seconds").ValueKind != JsonValueKind.Number ||
                !root.GetProperty("ttl_seconds").TryGetInt32(out int ttl) ||
                ttl < 1 || ttl > 600)
                return Hold("HOLD_TTL");
            if (root.GetProperty("observed_at_utc").ValueKind != JsonValueKind.String)
                return Hold("HOLD_TIME");
            string? at = root.GetProperty("observed_at_utc").GetString();
            if (at is null || !UtcShape.IsMatch(at) ||
                !DateTimeOffset.TryParseExact(at, new[] {
                    "yyyy-MM-dd'T'HH:mm:ss'Z'", "yyyy-MM-dd'T'HH:mm:ss.FFFFFFF'Z'"
                }, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out var observed))
                return Hold("HOLD_TIME");
            var age = now - observed.ToUniversalTime();
            if (age.TotalSeconds < -30)
                return Hold("HOLD_FUTURE_SOURCE");
            if (age.TotalSeconds > ttl)
                return Hold("HOLD_STALE_SOURCE");
            return new MuleState("SOURCE_FRESH__RECEIVER_UNVERIFIED", workId, true);
        }
        catch (JsonException)
        {
            return Hold("HOLD_JSON");
        }
        catch (InvalidOperationException)
        {
            return Hold("HOLD_FIELD_TYPES");
        }
    }
}
