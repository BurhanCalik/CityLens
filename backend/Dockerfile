# CityLens backend (masterfabric-go architecture) — built for Render (Docker runtime).
#
# IMPORTANT: the Go version MUST satisfy go.mod (go 1.25.x). Using golang:1.22
# here makes Render fail the build with "go.mod requires go >= 1.25.x".
FROM golang:1.25-alpine AS builder

RUN apk add --no-cache git ca-certificates

WORKDIR /app

# Cache module downloads.
COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Static binary. detections.json is embedded via go:embed, so no data file copy
# is required at runtime — the endpoint works even with no database.
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -o /bin/citylens ./cmd/server

# ---- Runtime ----
FROM alpine:3.20

RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

COPY --from=builder /bin/citylens /app/citylens
COPY --from=builder /app/internal/infrastructure/postgres/migrations /app/migrations

# Render injects PORT and the config reads it (PORT -> SERVER_PORT -> 8080).
ENV SERVER_HOST=0.0.0.0
EXPOSE 8080

ENTRYPOINT ["/app/citylens"]
