package usecase

import (
	"context"
	"testing"

	"github.com/masterfabric-go/masterfabric/internal/domain/detection/model"
)

type fakeRepo struct{ items []*model.Detection }

func (f *fakeRepo) List(_ context.Context) ([]*model.Detection, error) { return f.items, nil }

func TestDetectionStats(t *testing.T) {
	repo := &fakeRepo{items: []*model.Detection{
		{Label: "trafik levhası", Score: 0.9, Severity: model.SeverityUrgent},
		{Label: "trafik levhası", Score: 0.5, Severity: model.SeverityWarning},
		{Label: "çöp kutusu", Score: 0.7, Severity: model.SeverityInfo},
	}}
	uc := NewDetectionStatsUseCase(repo)

	stats, err := uc.Execute(context.Background())
	if err != nil {
		t.Fatalf("Execute: %v", err)
	}
	if stats.Total != 3 {
		t.Errorf("Total = %d, want 3", stats.Total)
	}
	if stats.ByLabel["trafik levhası"] != 2 {
		t.Errorf("ByLabel[trafik levhası] = %d, want 2", stats.ByLabel["trafik levhası"])
	}
	if stats.BySeverity["urgent"] != 1 {
		t.Errorf("BySeverity[urgent] = %d, want 1", stats.BySeverity["urgent"])
	}
	wantAvg := (0.9 + 0.5 + 0.7) / 3.0
	if diff := stats.AvgScore - wantAvg; diff < -1e-9 || diff > 1e-9 {
		t.Errorf("AvgScore = %f, want %f", stats.AvgScore, wantAvg)
	}
}

func TestDetectionStatsEmpty(t *testing.T) {
	uc := NewDetectionStatsUseCase(&fakeRepo{})
	stats, err := uc.Execute(context.Background())
	if err != nil {
		t.Fatalf("Execute: %v", err)
	}
	if stats.Total != 0 || stats.AvgScore != 0 {
		t.Errorf("empty stats wrong: %+v", stats)
	}
}
