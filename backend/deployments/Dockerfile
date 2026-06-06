# Build stage
# NOTE: Go version MUST match go.mod (go 1.25.x). golang:1.22 breaks the build.
FROM golang:1.25-alpine AS builder

RUN apk add --no-cache git ca-certificates

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o /bin/masterfabric ./cmd/server

# Runtime stage
FROM alpine:3.20

RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

COPY --from=builder /bin/masterfabric /app/masterfabric
COPY --from=builder /app/internal/infrastructure/postgres/migrations /app/migrations

EXPOSE 8080

ENTRYPOINT ["/app/masterfabric"]
