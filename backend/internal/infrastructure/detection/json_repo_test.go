package detection

import (
	"context"
	"testing"

	"github.com/google/uuid"
)

func TestEmbeddedDetectionsLoad(t *testing.T) {
	repo, err := NewJSONRepository("", nil)
	if err != nil {
		t.Fatalf("NewJSONRepository: %v", err)
	}
	items, err := repo.List(context.Background())
	if err != nil {
		t.Fatalf("List: %v", err)
	}
	if len(items) == 0 {
		t.Fatal("expected embedded detections, got 0")
	}
	for i, d := range items {
		if d.ID == uuid.Nil {
			t.Errorf("detection %d has nil ID (should be assigned a stable UUID)", i)
		}
		if d.Severity == "" {
			t.Errorf("detection %d has empty severity (should default to info)", i)
		}
	}
}

func TestFallbackToEmbeddedOnBadPath(t *testing.T) {
	// A non-existent DETECTIONS_PATH must NOT fail — it falls back to embedded.
	repo, err := NewJSONRepository("does-not-exist-12345.json", nil)
	if err != nil {
		t.Fatalf("expected embedded fallback, got error: %v", err)
	}
	items, err := repo.List(context.Background())
	if err != nil {
		t.Fatalf("List: %v", err)
	}
	if len(items) == 0 {
		t.Fatal("expected embedded fallback detections, got 0")
	}
}

func TestStableIDsAreDeterministic(t *testing.T) {
	a, _ := NewJSONRepository("", nil)
	b, _ := NewJSONRepository("", nil)
	itemsA, _ := a.List(context.Background())
	itemsB, _ := b.List(context.Background())
	if len(itemsA) != len(itemsB) || len(itemsA) == 0 {
		t.Fatalf("unexpected counts: %d vs %d", len(itemsA), len(itemsB))
	}
	if itemsA[0].ID != itemsB[0].ID {
		t.Errorf("IDs are not stable across loads: %s vs %s", itemsA[0].ID, itemsB[0].ID)
	}
}
