// mongo_queries.js
// In mongosh, run load("mongo_queries.js") to execute these queries and print their runtimes.

// Helper: timing wrapper
function timeQuery(label, fn) {
    const start = Date.now();
    const cursor = fn();
    // Force materialization so the query fully executes on the server
    if (cursor && typeof cursor.toArray === "function") {
      cursor.toArray();
    }
    const end = Date.now();
    print(label + " execution time: " + (end - start) + " ms");
  }
  
  // Assume we are already using the ecommerce database
  db = db.getSiblingDB("ecommerce");
  
  //  Query 2: Last 5 products viewed by a user in the past 6 months 
  // Note: we use user_id = 1 as a "test user"; in the report you can treat this as Sarah's ID (e.g., looked up from the users table).
  function runQuery2() {
    const userId = 1; // assume user 1
  
    return db.events.aggregate([
      {
        $match: {
          user_id: userId,
          event_type: "product_view",
          timestamp: {
            // last 6 months
            $gte: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000)
          }
        }
      },
      { $sort: { timestamp: -1 } },
      {
        $group: {
          _id: "$product_id",
          last_viewed_at: { $first: "$timestamp" }
        }
      },
      { $sort: { last_viewed_at: -1 } },
      { $limit: 5 }
    ]);
  }
  
  //  Query 4: Products in the fashion category with color=blue or size=L (Mongo attribute part) 
  function runQuery4() {
    // In the generated data, fashion has category_id = 1
    return db.products.find(
      {
        category_id: 1,
        $or: [
          { "attributes.color": "blue" },
          { "attributes.size": "L" }
        ]
      },
      {
        product_id: 1,
        "attributes.size": 1,
        "attributes.color": 1,
        _id: 0
      }
    );
  }
  
  //  Query 5: Page view count per product, ordered by popularity (descending) 
  function runQuery5() {
    return db.events.aggregate([
      { $match: { event_type: "product_view" } },
      {
        $group: {
          _id: "$product_id",
          view_count: { $sum: 1 }
        }
      },
      { $sort: { view_count: -1 } }
    ]);
  }
  
  //  Query 6: A user's search terms over the last 30 days, grouped by time-of-day and frequency 
  function runQuery6() {
    const userId = 1; // same test user
  
    return db.events.aggregate([
      {
        $match: {
          user_id: userId,
          event_type: "search",
          timestamp: {
            $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
          }
        }
      },
      {
        $project: {
          term: "$query_string",
          hour: { $hour: "$timestamp" }
        }
      },
      {
        $project: {
          term: 1,
          time_of_day: {
            $switch: {
              branches: [
                {
                  case: {
                    $and: [
                      { $gte: ["$hour", 6] },
                      { $lt: ["$hour", 12] }
                    ]
                  },
                  then: "morning"
                },
                {
                  case: {
                    $and: [
                      { $gte: ["$hour", 12] },
                      { $lt: ["$hour", 18] }
                    ]
                  },
                  then: "afternoon"
                },
                {
                  case: {
                    $and: [
                      { $gte: ["$hour", 18] },
                      { $lt: ["$hour", 24] }
                    ]
                  },
                  then: "evening"
                }
              ],
              default: "night"
            }
          }
        }
      },
      {
        $group: {
          _id: { term: "$term", time_of_day: "$time_of_day" },
          frequency: { $sum: 1 }
        }
      },
      { $sort: { frequency: -1 } }
    ]);
  }
  
  //  Helper: run all Mongo-related queries once and time them 
  function runAllMongoQueries() {
    print("=== Mongo performance test started ===");
    timeQuery("Query 2 (last 5 viewed products)", runQuery2);
    timeQuery("Query 4 (fashion & blue/L)", runQuery4);
    timeQuery("Query 5 (page views per product)", runQuery5);
    timeQuery("Query 6 (search terms by time-of-day)", runQuery6);
    print("=== Mongo performance test finished ===");
  }
  